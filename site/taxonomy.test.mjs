import test from 'node:test';
import assert from 'node:assert/strict';
import {naturalCompare, targetKey, assertUnique, assertTarget, entrySections, validateTaxonomy} from './taxonomy.mjs';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const registry=read('data/learning-taxonomy.json'),index=read('content-index.json'),hot=read('docs/80-hot100/manifest.json'),supplement=read('data/reading-catalog.json').supplementaryProblems;
const context={window:{}};
const shell=fs.readFileSync(path.join(root,'site/index.html'),'utf8');
for(const m of shell.matchAll(/src="(assets\/data\.[^"]+\.js)"/g))vm.runInNewContext(fs.readFileSync(path.join(root,'site',m[1]),'utf8'),context);
vm.runInNewContext(fs.readFileSync(path.join(root,'site/assets/data.js'),'utf8'),context);
const data=context.window.STUDY_DATA;
const {catalogue,create}=createRequire(import.meta.url)('./assets/search.js');
const projectPath='docs/50-projects/source-code-interview-deep-dive.md';
const entries=catalogue(data),engine=create(entries),query=p=>engine.query(new URLSearchParams(p)).results;

test('natural question order preserves full prefix and all numeric segments',()=>{
  assert.deepEqual(['A10','A2','A01'].sort(naturalCompare),['A01','A2','A10']);
  assert.deepEqual(['SC-B14','SC-A12','SC-B01','SC-A01','SC-A02'].sort(naturalCompare),['SC-A01','SC-A02','SC-A12','SC-B01','SC-B14']);
  assert.deepEqual(['SP-R2-10','SP-R1-10','SP-R2-2','SP-R1-2'].sort(naturalCompare),['SP-R1-2','SP-R1-10','SP-R2-2','SP-R2-10']);
});

test('original simulation fixture follows visible 1,2,3,4; anchors stay opaque',()=>{
  // This small fixture complements the actual registry ordering check below.
  const entries=[{title:'模拟追问 2',anchor:'stable-b'},{title:'模拟追问 1',anchor:'stable-a'},{title:'模拟追问 4',anchor:'stable-d'},{title:'模拟追问 3',anchor:'stable-c'}];
  const originalTargets=entries.map(x=>x.anchor).sort();
  const ordered=[...entries].sort((a,b)=>naturalCompare(a.title,b.title));
  assert.deepEqual(ordered.map(x=>x.title),['模拟追问 1','模拟追问 2','模拟追问 3','模拟追问 4']);
  assert.deepEqual(ordered.map(x=>x.anchor).sort(),originalTargets);
});

test('canonical targets and uniqueness retain exact IDs and anchors',()=>{
  assert.equal(targetKey('docs/example.md','a02'),'docs/example.md#a02');
  assert.equal(targetKey('docs/example.md'),'docs/example.md');
  assert.throws(()=>assertUnique(['A02','A02'],'题号'),/重复/);
  assert.doesNotThrow(()=>assertUnique(['A02','A2'],'literal ID'));
});

test('anchored search includes its nested answers but excludes next question',()=>{
  const doc={path:'docs/example.md',headings:[{id:'title',level:1},{id:'a01',level:3},{id:'answer',level:4},{id:'a02',level:3}],sections:[{id:'title',text:'intro'},{id:'a01',text:'question'},{id:'answer',text:'answer'},{id:'a02',text:'next question'}]};
  assert.deepEqual(entrySections(doc,'a01').map(s=>s.id),['a01','answer']);
  assert.equal(assertTarget(new Map([[doc.path,doc]]),doc.path,'a01'),doc);
  assert.throws(()=>assertTarget(new Map([[doc.path,doc]]),doc.path,'missing'),/缺少锚点/);
  assert.throws(()=>assertTarget(new Map(),doc.path),/缺少正文/);
});

test('actual registry preserves all 464 IDs and targets with focused teaching pages',()=>{
  assert.equal(JSON.stringify(data.taxonomy),JSON.stringify(registry));
  assert.equal(registry.pages.length,263);assert.equal(new Set(registry.pages.map(p=>p.path)).size,263);
  assert.deepEqual(registry.entries.filter(e=>e.itemId).map(e=>e.itemId).sort(),index.items.map(i=>i.id).sort());
  for(const item of index.items){const entry=registry.entries.find(e=>e.itemId===item.id);assert.equal(targetKey(entry.path,entry.anchor),targetKey(item.path,item.anchor||''));}
  assert.equal(registry.entries.filter(e=>e.itemId&&e.area==='qa').length,297);
  assert.equal(registry.entries.filter(e=>e.itemId&&e.subcategory==='projects').length,40);
  assert.equal(registry.entries.filter(e=>e.itemId&&e.area==='algorithms').length,127);
  assert.equal(registry.pages.filter(p=>p.path===projectPath).length,1);
  assert.equal(registry.pages.filter(p=>p.path!==projectPath).length,262);
  assert.equal(registry.entries.length,732);
});

test('real question and scenario display order preserves prefix and local sequence',()=>{
  for(const sub of registry.areas.find(a=>a.id==='qa').subcategories){const ids=query({area:'qa',subcategory:sub.id}).filter(r=>r.d.itemId).map(r=>r.d.itemId);assert.deepEqual(ids,[...ids].sort(naturalCompare));}
  const scenes=query({area:'interviews',subcategory:'scenarios'}).filter(r=>r.d.scenarioCardId).map(r=>r.d.scenarioCardId);
  assert.deepEqual(scenes,[...scenes].sort(naturalCompare));assert.equal(scenes.length,26);
  const sp=query({area:'interviews',subcategory:'shopee'}).filter(r=>r.d.id.startsWith('SP-')).map(r=>r.d.id);assert.equal(sp.length,34);assert.deepEqual(sp,[...sp].sort(naturalCompare));
  const simulations=query({area:'interviews',subcategory:'simulation'}).map(r=>Number(r.d.title.match(/模拟追问\s*(\d+)/)[1]));assert.deepEqual(simulations,[1,2,3,4]);
  for(const category of hot.categories){const ids=query({area:'algorithms',subcategory:'hot-'+category.order}).filter(r=>r.d.problemId).map(r=>r.d.problemId);assert.deepEqual(ids,category.problem_ids);}
});

test('legacy supplemental listing, LC77, topic and difficulty use real navigation catalogue',()=>{
  assert.equal(query({module:'supplement'}).length,15);
  assert.equal(query({module:'supplement',q:'LC77'})[0].d.targetAnchor,'problem-77');
  assert.equal(query({module:'supplement',q:'LC77'})[0].d.resourceProblemId,77);
  for(const difficulty of ['EASY','MEDIUM','HARD'])assert.equal(query({module:'supplement',difficulty}).length,supplement.filter(r=>r.difficulty===difficulty).length);
  for(const topic of new Set(supplement.map(r=>r.topic)))assert.equal(query({module:'supplement',topic}).length,supplement.filter(r=>r.topic===topic).length);
});

test('global search deduplicates canonical target while preserving separate questions',()=>{
  for(const q of ['A01','RAG','SQL','LC77','Go']){const results=query({q});const keys=results.map(({d,section})=>targetKey(d.path,d.targetAnchor||section?.id||''));assert.equal(new Set(keys).size,keys.length,q);}
  assert.equal(query({q:'A01'})[0].d.itemId,'A01');
  const qa=query({area:'qa'});assert.equal(qa.length,322);assert.equal(qa.filter(r=>r.d.itemId).length,297);assert.ok(qa.some(r=>r.d.itemId==='A01'));assert.ok(qa.some(r=>r.d.itemId==='A02'));
  const saved=create(entries).query(new URLSearchParams({view:'saved'}),{saved:['docs/10-agent/01-agent-loop-tools-and-state.md'],done:[]}).results;assert.equal(saved.length,1);assert.equal(saved[0].d.targetAnchor,'');
});

test('interview filters retain mixed-company and aggregate-round boundaries',()=>{
  assert.equal(registry.entries.filter(e=>e.kind==='interview').length,27);
  const mixed=registry.entries.filter(e=>e.kind==='interview'&&e.subcategory==='mixed');assert.equal(mixed.length,3);
  for(const e of mixed)for(const company of e.companies)assert.ok(query({area:'interviews',company}).some(r=>r.d.id===e.id&&r.d.notice.includes('不逐一归属')));
  for(const e of registry.entries.filter(e=>e.roundLabel==='一/二面综合回顾'))for(const round of ['1','2'])assert.ok(!query({area:'interviews',round}).some(r=>r.d.id===e.id));
  for(const e of registry.entries.filter(e=>e.kind==='simulation')){assert.ok(!e.companies);assert.ok(!e.rounds);}
  for(const id of ['report:P18','report:P19']){const e=registry.entries.find(e=>e.id===id);assert.deepEqual(e.companies,['bytedance']);assert.deepEqual(e.rounds,[1]);assert.ok(/^p1[89]-answers$/.test(e.anchor));}
});

test('algorithm theme and method are distinct, reviewed relations do not invent sameness',()=>{
  const get=id=>registry.entries.find(e=>e.itemId==='LC'+id);
  assert.ok(get(76).patterns.includes('滑动窗口'));assert.ok(get(136).patterns.includes('位操作'));assert.deepEqual(get(53).patterns,['动态规划']);assert.deepEqual(get(208).patterns,['前缀检索']);assert.ok(get(53).method.includes('Kadane'));assert.ok(get(136).method.includes('异或'));assert.ok(get(208).method.includes('Trie'));assert.deepEqual(get(5).patterns,['中心扩展']);
  assert.notDeepEqual(get(207).patterns,get(994).patterns);assert.notDeepEqual(get(208).patterns,get(207).patterns);
  for(const [a,b]of [[208,207],[208,994],[41,53],[53,56],[56,189],[189,238],[31,75],[75,136],[169,287]])assert.ok(!registry.related[get(a).path].some(l=>l.path===get(b).path&&/同模式|同方法/.test(l.relation)));
});

test('every page has small valid related set and public registry excludes audit fields',()=>{
  const docs=new Map(data.docs.map(d=>[d.path,d]));
  for(const page of registry.pages){const links=registry.related[page.path];assert.ok(links.length>=1&&links.length<=3,page.path);for(const link of links){assertTarget(docs,link.path,link.anchor);assert.ok(!(link.path===registry.guidePath&&!link.anchor));assert.ok(!/基线|审核|已核实来源/.test(link.relation+link.label));}}
  const forbidden=new Set(['evidence','scope','company_scope','round_scope','sourceUrl','rawMarkdown','author','audit','designscope']);
  const inspect=x=>{if(!x||typeof x!=='object')return;for(const [key,value]of Object.entries(x)){assert.ok(!forbidden.has(key),key);inspect(value);}};inspect(registry);
});

test('data structure and algorithm pattern filters are independent of 17 themes',()=>{
  assert.equal(registry.areas.find(a=>a.id==='algorithms').subcategories.filter(s=>s.id.startsWith('hot-')).length,17);
  assert.deepEqual(query({area:'algorithms',structure:'字典树'}).map(r=>r.d.itemId),['LC208']);
  const binary=query({area:'algorithms',pattern:'二分查找'}).map(r=>r.d.itemId);assert.ok(binary.includes('LC300'));assert.ok(binary.includes('LC35'));
  assert.deepEqual(query({area:'algorithms',pattern:'中心扩展'}).map(r=>r.d.itemId),['LC5']);
  assert.ok(query({area:'algorithms',subcategory:'hot-9',pattern:'前缀检索'}).some(r=>r.d.itemId==='LC208'));
  assert.ok(!query({area:'algorithms',pattern:'动态规划'}).some(r=>r.d.itemId==='LC5'||r.d.itemId==='LC300'));
});


test('saved and done filter any matching chapter entry before canonical-path deduplication',()=>{
  const qa=registry.entries.find(e=>e.itemId==='A01'),report=registry.entries.find(e=>e.id==='report:P18');
  const state={saved:[qa.path,report.path],done:[qa.path,report.path]},engine=create(entries);
  for(const view of ['saved','done']){
    const run=filters=>engine.query(new URLSearchParams({view,...filters}),state).results;
    assert.equal(run({}).length,2);
    const questions=run({area:'qa'});assert.equal(questions.length,1);assert.equal(questions[0].d.path,qa.path);assert.ok(questions[0].d.targetAnchor);
    const reports=run({area:'interviews',company:'bytedance',round:'1'});assert.equal(reports.length,1);assert.equal(reports[0].d.path,report.path);assert.ok(['p18-answers','p19-answers'].includes(reports[0].d.targetAnchor));
    assert.equal(run({area:'interviews',company:'bytedance',round:'2'}).length,0);
    for(const filters of [{q:'Agent'},{area:'interviews'},{area:'qa'},{area:'interviews',company:'bytedance'}]){const rows=run(filters);assert.equal(new Set(rows.map(r=>r.d.path)).size,rows.length);}
  }
  assert.deepEqual(state,{saved:[qa.path,report.path],done:[qa.path,report.path]});
});


test('all 163 non-Hot100 pages link to substantive cross-page teaching sections',()=>{
  const docs=new Map(data.docs.map(d=>[d.path,d]));
  const pages=registry.pages.filter(p=>!p.path.startsWith('docs/80-hot100/problems/'));assert.equal(pages.length,163);
  for(const page of pages){
    const links=registry.related[page.path];assert.ok(links.some(l=>l.path!==page.path),page.path);
    for(const link of links){
      assert.ok(link.anchor,page.path);assertTarget(docs,link.path,link.anchor);
      assert.ok(link.description?.length>=12,page.path);assert.notEqual(link.relation,'延伸理解');
      assert.ok(!/^(?:README|[a-z0-9]+(?:-[a-z0-9]+)+)(?:\.md)?$/.test(link.label),link.label);
      assert.ok(!/A39[–—-]A44|B21[–—-]B35/.test(link.label),link.label);
      assert.ok(link.path!=='QUESTION_INDEX.md'||link.anchor,page.path);
    }
  }
  const categoryLinks=pages.filter(p=>p.path.startsWith('docs/80-hot100/categories/')).flatMap(p=>registry.related[p.path]);
  assert.equal(new Set(categoryLinks.map(l=>l.description)).size,categoryLinks.length);
  assert.ok(categoryLinks.every(l=>!l.description.includes('本题方法：')));
  const recovery=registry.related['docs/40-backend/41-storage-recovery-followups.md'];assert.deepEqual(recovery.map(l=>l.anchor),['b34','b35','b17']);
  assert.ok(registry.related['docs/90-public-interview-scenarios/sc-a06.md'].some(l=>l.anchor==='a20'));
  assert.ok(registry.related['docs/90-public-interview-scenarios/sc-b04.md'].some(l=>l.anchor==='j21'));
  assert.ok(registry.related['docs/90-public-interview-scenarios/sc-a07.md'].some(l=>l.anchor==='tool-result-contract'));
});

test('stable original ID sequences preserve existing gaps without inventing questions',()=>{
  const ids=registry.entries.filter(e=>e.itemId).map(e=>e.itemId);assert.equal(new Set(ids).size,464);
  const numbers=prefix=>ids.filter(id=>new RegExp('^'+prefix+'\\d+$').test(id)).map(id=>Number(id.slice(prefix.length))).sort((a,b)=>a-b);
  const range=(first,last)=>Array.from({length:last-first+1},(_,i)=>first+i);
  assert.deepEqual(numbers('A'),[...range(1,30),...range(39,47)]);
  assert.deepEqual(numbers('FA'),[...range(22,43),63]);
  for(const [prefix,last] of Object.entries({J:46,FJ:46,G:40,B:50,FB:93,X:6,R:12,S:9}))assert.deepEqual(numbers(prefix),range(1,last),prefix);
  assert.deepEqual(numbers('LC'),hot.problems.map(p=>p.id).sort((a,b)=>a-b));
});


test('project depth uses exact approved text and existing heading targets without new question IDs',()=>{
  const bytes=fs.readFileSync(path.join(root,projectPath));
  assert.equal(bytes.length,96772);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),'2e4dbb057fa544ca83af5ab358547a18ca2acc6a87c27e39326357b688e52ec9');
  const text=bytes.toString('utf8');
  for(const version of ['9afe774372f2068eb7e57ecdf1c491965eace2e3','8abe80150be6fc72359f2fe78acfd5960d664bdf','bd0230f2f14b03fa016829cf895a4b009515e88c'])assert.ok(text.includes(version));
  const doc=data.docs.find(d=>d.path===projectPath);assert.equal(doc.headings.length,44);
  const rows=registry.entries.filter(e=>e.subcategory==='project-depth');assert.equal(rows.length,24);
  assert.equal(new Set(rows.map(e=>targetKey(e.path,e.anchor))).size,24);
  assert.equal(rows.filter(e=>e.kind==='chapter').length,1);assert.equal(rows.filter(e=>e.kind==='project-section').length,23);
  for(const e of rows){assert.equal(e.path,projectPath);assert.equal(e.area,'qa');assert.ok(!e.itemId&&!e.companies&&!e.rounds&&!e.roundLabel);assertTarget(new Map([[projectPath,doc]]),e.path,e.anchor);}
  for(let n=1;n<=12;n++){const e=rows.find(e=>e.anchor==='direction-'+String(n).padStart(2,'0'));assert.ok(e);assert.deepEqual(e.projects,n===10?['knowflow','researchpilot']:n<=7||n===12?['knowflow']:['researchpilot']);}
  assert.deepEqual(registry.projects,[{id:'knowflow',label:'KnowFlow'},{id:'researchpilot',label:'ResearchPilot'},{id:'shared',label:'共同练习'}]);
});

test('project filters include shared practice and saved state remains canonical-path based',()=>{
  const filters={area:'qa',subcategory:'project-depth'};
  assert.equal(query(filters).length,24);
  for(const [project,count]of Object.entries({knowflow:19,researchpilot:14,shared:8})){
    const results=query({...filters,project});assert.equal(results.length,count);
    assert.ok(results.every(r=>r.d.projects.includes(project)||r.d.projects.includes('shared')));
    assert.ok(results.every(r=>r.d.path===projectPath));
  }
  assert.equal(query({...filters,project:'unknown-project'}).length,0);
  const state={saved:[projectPath],done:[projectPath]};
  for(const view of ['saved','done'])for(const project of ['knowflow','researchpilot','shared']){
    const results=engine.query(new URLSearchParams({...filters,view,project}),state).results;
    assert.equal(results.length,1);assert.equal(results[0].d.path,projectPath);
  }
  assert.deepEqual(state,{saved:[projectPath],done:[projectPath]});
});

test('project schema rejects ambiguous ownership and accidental question or company labels',()=>{
  assert.doesNotThrow(()=>validateTaxonomy(registry,data.docs,index.items));
  for(const mutate of [
    r=>r.projects.push({...r.projects[0]}),
    r=>r.entries.find(e=>e.subcategory==='project-depth').projects=['missing'],
    r=>r.entries.find(e=>e.subcategory==='project-depth').projects=['shared','knowflow'],
    r=>r.entries.find(e=>e.subcategory==='project-depth').projects=['knowflow','knowflow'],
    r=>r.entries.find(e=>e.subcategory==='project-depth').companies=['bytedance'],
    r=>r.entries.find(e=>e.subcategory==='project-depth').rounds=[1],
    r=>r.entries.find(e=>e.subcategory==='project-depth').itemId='A48',
    r=>delete r.entries.find(e=>e.subcategory==='project-depth').projects
  ]){const copy=structuredClone(registry);mutate(copy);assert.throws(()=>validateTaxonomy(copy,data.docs,index.items));}
});

test('project footer offers precise prerequisites and four knowledge chapters link back',()=>{
  const links=registry.related[projectPath];assert.equal(links.length,3);
  assert.deepEqual(links.map(l=>l.anchor),['a27','核心思路','7-从涨了-10-个点走到可信的版本比较']);
  const backlinks=Object.entries(registry.related).flatMap(([from,links])=>links.filter(l=>l.path===projectPath).map(l=>({from,...l})));
  assert.equal(backlinks.length,4);
  assert.deepEqual(backlinks.map(l=>l.anchor).sort(),['direction-01','direction-02','direction-07','direction-11']);
  for(const link of backlinks){assert.equal(registry.pages.find(p=>p.path===link.from).area,'knowledge');assert.equal(registry.related[link.from].length,3);}
});


test('LC115 is a distinct non-Hot100 handwrite entry without changing numbered IDs',()=>{
  const record=registry.entries.find(e=>e.id==='extra:LC115');
  assert.equal(record.area,'algorithms');assert.equal(record.subcategory,'handwrite');
  assert.equal(record.anchor,'lc115');assert.equal(record.itemId,undefined);
  assert.deepEqual(record.questionIds,['LC115']);
  const results=query({area:'algorithms',subcategory:'handwrite',q:'LC115'});
  assert.equal(results[0].d.id,'extra:LC115');
  assert.equal(results[0].d.targetAnchor,'lc115');
  assert.ok(results[0].d.sections[0].text.includes('dp[j] += dp[j - 1]'));
  assert.ok(results[0].d.sections[0].text.includes('不计删除动作')||results[0].d.sections[0].text.includes('不区分删除动作'));
  assert.ok(!query({q:'X01'}).some(r=>r.d.id==='extra:LC115'));
  assert.equal(data.questionCount,464);assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);
  assert.equal(query({area:'algorithms',pattern:'动态规划',q:'LC115'})[0].d.id,'extra:LC115');
  assert.equal(new Set(registry.pages.filter(p=>p.path===registry.guidePath).map(p=>p.path)).size,1);
});


test('Text-to-SQL teaching has one canonical page, an unnumbered answer and working related anchors',()=>{
  const teachingPath='docs/10-agent/36-text-to-sql-agent.md';
  const docs=new Map(data.docs.map(d=>[d.path,d]));
  assert.equal(registry.pages.filter(p=>p.path===teachingPath).length,1);
  const records=registry.entries.filter(e=>e.path===teachingPath);
  assert.equal(records.length,2);assert.ok(records.every(e=>!e.itemId&&!e.companies&&!e.rounds));
  const answer=query({area:'qa',q:'Text-to-SQL'}).find(r=>r.d.id==='teaching:text-to-sql');
  assert.ok(answer);assert.equal(answer.d.targetAnchor,'text-to-sql-answer');
  assert.ok(query({area:'knowledge',q:'Text-to-SQL'}).some(r=>r.d.path===teachingPath));
  for(const link of registry.related[teachingPath])assertTarget(docs,link.path,link.anchor);
  const saved=create(entries).query(new URLSearchParams({view:'saved',q:'Text-to-SQL'}),{saved:[teachingPath],done:[]}).results;
  assert.equal(saved.length,1);assert.equal(saved[0].d.path,teachingPath);
  assert.equal(data.questionCount,464);assert.equal(data.hot100Count,100);
});
