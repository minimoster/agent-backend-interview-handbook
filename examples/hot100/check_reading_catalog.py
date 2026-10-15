"""Verify stable algorithm implementations and the independent teaching index."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def main():
    contracts = json.loads((ROOT / 'data/algorithm-contracts.json').read_text())
    manifest_path = ROOT / contracts['canonical_manifest_path']
    manifest = json.loads(manifest_path.read_text())
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == contracts['canonical_manifest_sha256']
    records = contracts['algorithms']
    assert len(records) == len({p['id'] for p in records}) == 100
    assert [p['id'] for p in records] == [p['id'] for p in manifest['problems']]
    assert len(manifest['categories']) == 17
    for record in records:
        source = (ROOT / record['python_path']).read_bytes()
        assert hashlib.sha256(source).hexdigest() == record['source_sha256'], record['id']
        assert (ROOT / record['doc_path']).is_file(), record['id']
    catalog = json.loads((ROOT / 'data/reading-catalog.json').read_text())
    supplement = catalog['supplementaryProblems']
    assert len(supplement) == len({p['id'] for p in supplement}) == 15
    assert not {p['id'] for p in records} & {p['id'] for p in supplement}
    for record in supplement:
        text = (ROOT / record['doc_path']).read_text()
        anchor = record['article_anchor']
        assert text.count(f'<a id="{anchor}"></a>') == 1, record['id']
        assert record['difficulty'] in {'EASY', 'MEDIUM', 'HARD'}
        section = text.split(f'<a id="{anchor}"></a>', 1)[1].split('<a id=', 1)[0]
        assert re.search(r'题意|题目', section), record['id']
        assert re.search(r'解析|思路|原理', section), record['id']
        assert re.search(r'答案|实现|解法', section), record['id']
    print('PASS: 100 unchanged algorithm implementations / 17 categories / 15 independent answered exercises')


if __name__ == '__main__':
    main()
