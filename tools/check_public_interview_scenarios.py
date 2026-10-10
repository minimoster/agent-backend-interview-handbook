#!/usr/bin/env python3
"""Repository-local contract checks; no external service or model calls."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'sources/public-interviews'
def read(name):return json.loads((S/name).read_text())
def stable(url):
 u=urlsplit(url);return (u.netloc.lower(),u.path.rstrip('/'))
catalog=read('source-catalog.json'); reports=catalog['records']; cards=read('scenario-map.json')['records']; manifest=read('manifest.json')
assert len(reports)==17 and len({stable(x['url']) for x in reports})==17
assert len({x['author'] for x in reports})==16
assert {x['id'] for x in reports if x['novelty']=='existing_public_page'}=={'P01','P03','P06'}
assert sum(x['novelty']=='new_public_page' for x in reports)==14
old_authors={x['author'] for x in reports if x['novelty']=='existing_public_page'}
assert len({x['author'] for x in reports}-old_authors)==13
base=json.loads((ROOT/'sources/catalog.json').read_text())
base_urls={stable(x['url']) for x in base if 'url' in x}
assert {x['id'] for x in reports if stable(x['url']) in base_urls}=={'P01','P03','P06'}
assert len(cards)==26 and {x['card_id'] for x in cards}=={f'SC-{kind}{i:02d}' for kind,n in [('A',12),('B',14)] for i in range(1,n+1)}
ids={x['id'] for x in reports}; official=read('official-references.json')
assert official['count']==41 and len({x['url'] for x in official['records']})==41
urls={x['url'] for x in official['records']}
for card in cards:
 text=(ROOT/card['file']).read_text()
 assert text.startswith('# '+card['card_id']+' ')
 assert all((ROOT/p).is_file() for p in card['handbook_relative_paths'])
 assert set(card['public_report_ids'])<=ids
 assert set(card['official_urls'])<=urls
 assert '## 参考答案' in text and '## 练习与验收' in text
 assert len(re.findall(r'^## 追问[12]：',text,re.M))==2
 for exercise in card['local_exercises']:assert (ROOT/exercise.split('#')[0]).is_file()
index=json.loads((ROOT/'content-index.json').read_text())
assert index['counts']['interview_questions']==361 and len(index['items'])==461
assert not any(i['id'].startswith('SC-') for i in index['items'])
assert len(json.loads((ROOT/'docs/80-hot100/manifest.json').read_text())['problems'])==100
assert len(json.loads((ROOT/'sources/carl-hot100-resources.json').read_text())['supplementary_index']['problems'])==15
model=json.loads((ROOT/'examples/public_interview_scenarios/evaluation_design_template.json').read_text())
assert model['status']=='design_only_not_executed' and len(model['cases'])==12
assert '不是防泄漏分组键' in model['split_policy']
assert manifest['counts']['original_scenario_cards']==26 and manifest['counts']['verified_xiaohongshu_platform_core_pages']==0
assert all(urlsplit(x['url']).netloc=='www.nowcoder.com' for x in reports)
assert sum(x.get('platform')=='小红书' for x in reports)==0
print('PASS: 17 public reports / 16 author labels / 14 new pages / 13 net-new author labels')
print('PASS: 26 independent scene cards / 41 official URLs / 4 Python exercises / 12 unexecuted model designs')
print('PASS: existing 361 lecture / 100 Hot100 / 15 external resource counts unchanged')
