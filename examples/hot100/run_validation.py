"""运行Hot100完整本地验证并更新机器可读结果，不做网络提交。"""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'docs/80-hot100/validation-result.json'


def main():
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    started = time.perf_counter()
    if not REPORT.exists():
        # 首次运行先建立报告目标，避免测试说明对结果文件的链接自引用断链。
        REPORT.write_text(json.dumps({"status": "running", "passed": False}) + "\n")
    inventory = subprocess.run(
        [sys.executable, '-B', 'examples/hot100/check_hot100.py'],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    try:
        inventory_result = json.loads(inventory.stdout)
    except json.JSONDecodeError:
        inventory_result = {'errors': ['完整性检查未产生合法JSON，请单独运行查看错误。']}
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests/hot100'), pattern='test_*.py')
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((ROOT / 'examples/hot100').glob('p[0-9]*.py'))
    }
    official = {}
    for path in sorted((ROOT / 'sources').glob('hot100-*-page-checks.json')):
        data = json.loads(path.read_text())
        rows = data.get('checks', data.get('problems', []))
        for row in rows:
            official[row['id']] = row
    expected_ids = {p['id'] for p in json.loads((ROOT / 'docs/80-hot100/manifest.json').read_text())['problems']}
    official_complete = set(official) == expected_ids
    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'python_version': platform.python_version(),
        'passed': inventory.returncode == 0 and result.wasSuccessful() and official_complete,
        'elapsed_seconds': round(time.perf_counter() - started, 3),
        'inventory': inventory_result,
        'unittest': {
            'test_cases_run': result.testsRun,
            'failures': [test.id() for test, _ in result.failures],
            'errors': [test.id() for test, _ in result.errors],
            'skipped': [test.id() for test, _ in result.skipped],
            'note': '测试入口数量不等于断言数量；每个入口可包含多个确定性用例及随机对拍。',
        },
        'official_problem_pages_recorded': len(official),
        'official_page_coverage_complete': official_complete,
        'source_sha256': hashes,
        'scope': '仅本地测试与静态检查；未向LeetCode提交，未声称在线AC，未测试所有合法输入。',
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(stream.getvalue())
    print(json.dumps({k: report[k] for k in ['passed', 'python_version', 'elapsed_seconds', 'official_problem_pages_recorded']}, ensure_ascii=False, indent=2))
    print('Report: docs/80-hot100/validation-result.json')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
