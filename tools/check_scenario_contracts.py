#!/usr/bin/env python3
"""Check teaching contracts without publishing provenance catalogs."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT / 'data/reading-catalog.json').read_text())
    cards = catalog['scenarios']
    expected = {f'SC-{kind}{i:02d}' for kind, n in [('A', 12), ('B', 14)] for i in range(1, n + 1)}
    assert len(cards) == 26 and {r['card_id'] for r in cards} == expected
    for card in cards:
        text = (ROOT / card['file']).read_text()
        assert text.startswith('# ' + card['card_id'] + ' ')
        assert '## 参考答案' in text or '## 答案' in text
        assert '## 练习与验收' in text
        assert len(re.findall(r'^## 追问[12]：', text, re.M)) == 2
    index = json.loads((ROOT / 'content-index.json').read_text())
    assert index['counts']['interview_questions'] == 364
    assert len(index['items']) == 464
    assert not any(r['id'].startswith('SC-') for r in index['items'])
    hot = json.loads((ROOT / 'docs/80-hot100/manifest.json').read_text())
    assert len(hot['problems']) == 100
    shopee = json.loads((ROOT / 'data/shopee-agent-question-map.json').read_text())
    assert shopee['unique_question_count'] == len(shopee['records']) == 34
    assert len({r['id'] for r in shopee['records']}) == 34
    chapter = (ROOT / 'docs/60-interviews/agent-followups-20261015.md').read_text()
    identifiers = re.findall(r'^#### (P(?:18|19)-\d{2}) ', chapter, re.M)
    assert identifiers == ([f'P18-{i:02d}' for i in range(1, 24)] + [f'P19-{i:02d}' for i in range(1, 12)])
    assert len(re.findall(r'^## S0[1-9] ', (ROOT / 'docs/70-practice/sql-nine-worked-problems.md').read_text(), re.M)) == 9
    model = json.loads((ROOT / 'examples/public_interview_scenarios/evaluation_design_template.json').read_text())
    assert model['status'] == 'design_only_not_executed' and len(model['cases']) == 12
    assert '不是防泄漏分组键' in model['split_policy']
    print('PASS: 26 answered scenarios / 34 answered Agent followups / 34专项 / 9 SQL / 464 index entries')


if __name__ == '__main__':
    main()
