"""验证官方100题清单、本地链接、逐题代码一致性及测试覆盖入口。

从仓库根目录执行：python examples/hot100/check_hot100.py
只读检查；不访问网络，不把本地结果等同于LeetCode判题结果。
"""
import ast
from collections import Counter
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/80-hot100'
REQUIRED = [
    '题意与接口', '从朴素方法到优化', '核心思路', '手推一个小例子',
    '为什么正确', 'Python 实现', '复杂度', '边界与易错点', '本地测试与复习',
]

def main():
    errors = []
    manifest = json.loads((DOCS / 'manifest.json').read_text())
    problems, categories = manifest['problems'], manifest['categories']
    ids = [p['id'] for p in problems]
    if len(ids) != 100 or len(set(ids)) != 100:
        errors.append('题号必须恰为100且不重复')
    if len({p['slug'] for p in problems}) != 100:
        errors.append('slug必须恰为100且不重复')
    if len(categories) != 17:
        errors.append('官方分类必须为17类')
    flattened = [pid for c in categories for pid in c['problem_ids']]
    if flattened != ids:
        errors.append('分类顺序与逐题顺序不一致')
    for category in categories:
        if category['count'] != len(category['problem_ids']):
            errors.append(f"分类计数错误：{category['name']}")
    expected_docs = {ROOT / p['doc_path'] for p in problems}
    expected_sources = {ROOT / p['python_path'] for p in problems}
    actual_docs = set((DOCS / 'problems').glob('*.md'))
    actual_sources = set((ROOT / 'examples/hot100').glob('p[0-9]*.py'))
    for kind, expected, actual in [('讲解', expected_docs, actual_docs), ('源码', expected_sources, actual_sources)]:
        for path in sorted(expected - actual):
            errors.append(f'缺少{kind}: {path.relative_to(ROOT)}')
        for path in sorted(actual - expected):
            errors.append(f'多余{kind}: {path.relative_to(ROOT)}')
    for p in problems:
        doc, source = ROOT / p['doc_path'], ROOT / p['python_path']
        if not doc.exists() or not source.exists():
            continue
        text, code = doc.read_text(), source.read_text()
        if not text.startswith(f"# {p['id']}. {p['title_zh']}"):
            errors.append(f"标题与清单不符：{p['id']}")
        for section in REQUIRED:
            if f'## {section}' not in text:
                errors.append(f"{p['id']}缺少段落：{section}")
        blocks = re.findall(r'```python\n(.*?)\n```', text, flags=re.S)
        # 源文件首行只是标题docstring，不属于判题算法主体。
        algorithm = '\n'.join(code.splitlines()[1:]).strip()
        if len(blocks) != 1 or blocks[0].strip() != algorithm:
            errors.append(f"{p['id']}文档代码块与实际源码不一致")
        if '#' not in code:
            errors.append(f"{p['id']}缺少解释算法状态/顺序的源码注释")
        try:
            tree = ast.parse(code)
            classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
            expected_class = {146: 'LRUCache', 155: 'MinStack', 208: 'Trie', 295: 'MedianFinder'}.get(p['id'], 'Solution')
            if expected_class not in classes:
                errors.append(f"{p['id']}缺接口类{expected_class}")
        except SyntaxError as error:
            errors.append(f"{p['id']}源码语法错误：{error.msg}")
    checked_links = 0
    markdown_files = list(DOCS.rglob('*.md')) + [ROOT / 'examples/hot100/README.md']
    for path in markdown_files:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            target = target.split('#', 1)[0]
            if not target or urlparse(target).scheme:
                continue
            resolved = (path.parent / unquote(target)).resolve()
            checked_links += 1
            if not resolved.exists():
                errors.append(f'本地断链：{path.relative_to(ROOT)} -> {target}')
    test_ids = set()
    test_methods = 0
    for path in (ROOT / 'tests/hot100').glob('test_*.py'):
        try:
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'):
                    test_methods += 1
                    match = re.match(r'test_p(\d{4})(?:_|$)', node.name)
                    if match:
                        test_ids.add(int(match.group(1)))
        except SyntaxError as error:
            errors.append(f'测试语法错误：{path.name}: {error.msg}')
    if set(ids) - test_ids:
        errors.append(f'没有逐题测试入口：{sorted(set(ids) - test_ids)}')
    if test_ids - set(ids):
        errors.append(f'题单外测试入口：{sorted(test_ids - set(ids))}')
    summary = {
        'problem_count': len(ids), 'unique_problem_count': len(set(ids)),
        'category_count': len(categories), 'doc_count': len(actual_docs),
        'python_module_count': len(actual_sources), 'tested_problem_entrypoints': len(test_ids),
        'test_method_count': test_methods, 'local_links_checked': checked_links,
        'errors': errors,
        'note': '本检查验证清单、语法、文档源码一致性、链接目标与测试入口；算法行为需另运行unittest。',
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
