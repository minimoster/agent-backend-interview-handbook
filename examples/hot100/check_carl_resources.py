"""Read-only verification of Carl links, scope, and preservation of original Hot100.

Run from the repository root: python -B examples/hot100/check_carl_resources.py
Uses public metadata in sources/carl-hot100-resources.json; needs no network.
External link availability is a dated observation, not a permanent guarantee.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
SHA = lambda value: hashlib.sha256(value).hexdigest()


def main():
    mapping = json.loads((ROOT / 'sources/carl-hot100-resources.json').read_text())
    manifest_path = ROOT / mapping['canonical_manifest_path']
    manifest = json.loads(manifest_path.read_text())
    problems = mapping['problems']
    supplement = mapping['supplementary_index']
    supplemental_problems = supplement['problems']
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    canonical_ids = [p['id'] for p in manifest['problems']]
    require(len(canonical_ids) == len(set(canonical_ids)) == 100, 'Hot100必须保持100个不同题号')
    require([p['id'] for p in problems] == canonical_ids, '资源映射必须与官方100题原顺序一致')
    require(len(manifest['categories']) == 17, 'Hot100必须保持17分类')
    require(SHA(manifest_path.read_bytes()) == mapping['canonical_manifest_original_sha256'], '官方manifest原始字节已改变')
    require(not supplement['counted_toward_canonical_hot100'], '补充题不得计入Hot100')
    require(len(supplemental_problems) == len({p['id'] for p in supplemental_problems}) == 15, '补充题必须为15个不同题号')
    require(not set(canonical_ids) & {p['id'] for p in supplemental_problems}, '补充题与官方Hot100出现重叠')

    source_count = article_count = link_count = 0
    for p in problems:
        source = (ROOT / p['python_path']).read_bytes()
        article = (ROOT / p['doc_path']).read_bytes()
        original_length = p['original_article_bytes']
        source_ok = SHA(source) == p['original_source_sha256']
        article_ok = SHA(article[:original_length]) == p['original_article_sha256']
        require(source_ok, f"{p['id']}原源码SHA256改变")
        require(article_ok, f"{p['id']}原文章前缀SHA256改变")
        source_count += int(source_ok)
        article_count += int(article_ok)
        addition = article[original_length:].decode()
        require(addition.startswith('\n## 代码随想录延伸阅读\n'), f"{p['id']}追加区块不完整")
        require('```' not in addition, f"{p['id']}外部资源区不应复制代码块")
        for key in ['primary_explanation_url', 'primary_python_url', 'primary_video_url']:
            require(not p[key] or p[key] in addition, f"{p['id']}正文缺少{key}")
        if not p['has_direct_explanation']:
            require('本次' in addition and '未找到' in addition and '不代表永久不存在' in addition,
                    f"{p['id']}缺少限定范围的缺失说明")

    for p in problems + supplemental_problems:
        require(p['has_direct_explanation'] == bool(p['primary_explanation_url']), f"{p['id']}讲解标志与URL不一致")
        require(p['has_direct_python_implementation'] == bool(p['primary_python_url']), f"{p['id']}Python标志与URL不一致")
        require(p['has_direct_official_video'] == bool(p['direct_videos']), f"{p['id']}视频标志与直接列表不一致")
        require(p['has_direct_official_video'] == bool(p['primary_video_url']), f"{p['id']}视频标志与主URL不一致")
        for related, videos in [(False, p['direct_videos']), (True, p['related_videos'])]:
            for v in videos:
                require(v['direct_problem_match'] == (not related), f"{p['id']}直接/相关视频分类不一致")
                require(v['author_mid'] == '525438321' and v['official_author_verified'], f"{p['id']}视频作者未核验")
                require(v['video_page_http_status'] == 200, f"{p['id']}视频读取状态非200")
        for key in ['primary_explanation_url', 'primary_python_url']:
            require(not p[key] or urlparse(p[key]).hostname == 'programmercarl.com', f"{p['id']}官网资源域名异常")
        require(not p['primary_video_url'] or urlparse(p['primary_video_url']).hostname == 'www.bilibili.com',
                f"{p['id']}视频域名异常")

    expected_main = (68, 67, 42)
    expected_supplement = (15, 15, 14)
    keys = ['has_direct_explanation', 'has_direct_python_implementation', 'has_direct_official_video']
    main_counts = tuple(sum(p[k] for p in problems) for k in keys)
    supplemental_counts = tuple(sum(p[k] for p in supplemental_problems) for k in keys)
    require(main_counts == expected_main, 'Hot100资源覆盖数与核验记录不一致')
    require(supplemental_counts == expected_supplement, '补充题资源覆盖数与核验记录不一致')
    require(mapping['coverage']['direct_explanation_problem_count'] == main_counts[0], '讲解汇总不一致')
    require(mapping['coverage']['direct_python_problem_count'] == main_counts[1], 'Python汇总不一致')
    require(mapping['coverage']['direct_official_video_problem_count'] == main_counts[2], '视频汇总不一致')
    require(supplement['coverage']['current_manifest_overlap_count'] == 0, '重叠汇总不一致')

    supplemental_doc = ROOT / 'docs/85-algorithm-supplement/README.md'
    supplemental_text = supplemental_doc.read_text()
    for p in supplemental_problems:
        anchor = p['article_anchor']
        require(supplemental_text.count(f'<a id="{anchor}"></a>') == 1, f"{p['id']}补充题锚点缺失或重复")
        require(p['article_url'] == f"{p['doc_path']}#{anchor}", f"{p['id']}补充题章节URL不一致")
        require(p['difficulty'] in ['EASY', 'MEDIUM'], f"{p['id']}补充题难度缺失")
        require(urlparse(p['difficulty_source_url']).hostname == 'leetcode.com', f"{p['id']}补充题难度来源异常")
        require(not p['in_current_canonical_hot100'], f"{p['id']}补充题范围标记异常")
        for key in ['primary_explanation_url', 'primary_python_url', 'primary_video_url']:
            require(not p[key] or p[key] in supplemental_text, f"{p['id']}补充题正文缺少{key}")

    for path in [supplemental_doc, ROOT / 'sources/carl-hot100-resources.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            parsed = urlparse(target)
            if parsed.scheme:
                continue
            local, _, fragment = target.partition('#')
            destination = (path.parent / unquote(local)).resolve() if local else path
            link_count += 1
            require(destination.exists(), f'本地链接目标不存在: {path.relative_to(ROOT)} -> {target}')
            if fragment and destination == supplemental_doc:
                require(f'<a id="{fragment}"></a>' in supplemental_text, f'补充题锚点不存在: {fragment}')

    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)

    require(not any(value.startswith('/') or value.startswith('file:') for value in strings(mapping)),
            '来源映射只应包含公开URL与仓库相对路径')
    report = {
        'canonical_hot100_problem_count': len(canonical_ids),
        'original_source_sha256_preserved_count': source_count,
        'original_article_prefix_sha256_preserved_count': article_count,
        'canonical_manifest_sha256_preserved': SHA(manifest_path.read_bytes()) == mapping['canonical_manifest_original_sha256'],
        'main_resource_counts_explanation_python_video': main_counts,
        'supplemental_problem_count': len(supplemental_problems),
        'supplemental_resource_counts_explanation_python_video': supplemental_counts,
        'supplemental_unique_anchor_count': len({p['article_anchor'] for p in supplemental_problems}),
        'additional_local_links_checked': link_count,
        'errors': errors,
        'scope': 'read-only local metadata and byte-preservation checks; dated external checks are not rerun',
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
