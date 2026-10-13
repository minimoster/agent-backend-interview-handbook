#!/usr/bin/env node
/** Non-rendering checks only; this does not claim actual browser/viewport QA. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {Marked} from './vendor/marked.mjs';

const site=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(site);
execFileSync(process.execPath,[path.join(site,'build.mjs'),'--check'],{stdio:'inherit'});
const context={window:{}};
const dataText=fs.readFileSync(path.join(site,'assets/data.js'),'utf8');
const html=fs.readFileSync(path.join(site,'index.html'),'utf8');
for(const match of html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g))vm.runInNewContext(fs.readFileSync(path.join(site,match[1]),'utf8'),context,{timeout:10000});
vm.runInNewContext(dataText,context,{timeout:10000});
const data=context.window.STUDY_DATA;
const docs=new Map(data.docs.map(d=>[d.path,d]));
const index=JSON.parse(fs.readFileSync(path.join(root,'content-index.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8'));
const require=createRequire(import.meta.url);
const {create,normalize}=require('./assets/search.js');
const engine=create(data.docs);
const fullEngine=create([...data.docs,...(data.supplementaryResources||[])]);
const carl=JSON.parse(fs.readFileSync(path.join(root,'sources/carl-hot100-resources.json'),'utf8'));
let checks=0;
const check=(name,fn)=>{fn();checks++;console.log(`PASS ${name}`);};
const relativeLuminance=hex=>{
  const channel=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(c=>c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4);
  return channel[0]*0.2126+channel[1]*0.7152+channel[2]*0.0722;
};
const contrastRatio=(foreground,background)=>{
  const a=relativeLuminance(foreground),b=relativeLuminance(background);
  return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
};

check('索引 461 项与 Hot100 100 题均有阅读文档',()=>{
  assert.equal(data.questionCount,index.items.length);
  assert.equal(data.hot100Count,manifest.problems.length);
  assert.equal(data.docs.filter(d=>d.problemId).length,100);
  for(const item of index.items){const d=docs.get(item.relative_path||item.path);assert.ok(d,`${item.id} 路径缺失`);if(item.anchor)assert.ok(d.headings.some(h=>h.id===item.anchor),`${item.id} 锚点缺失：${item.anchor}`);}
});
check('阅读产物逐篇保留当前 Markdown 原文',()=>{
  for(const d of data.docs)assert.equal(d.source,fs.readFileSync(path.join(root,d.path),'utf8'),d.path);
});
check('小分片可逐个审阅并完整还原阅读数据',()=>{
  const scripts=[...html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g)].map(m=>m[1]);
  assert.ok(scripts.length>100);
  const filenames=new Set(scripts);
  assert.equal(filenames.size,scripts.length);
  for(const file of scripts){
    const bytes=fs.readFileSync(path.join(site,file));
    assert.ok(bytes.length<=100000,`${file}: 分片超过100KB`);
    assert.equal(Buffer.from(bytes.toString('utf8'),'utf8').length,bytes.length,`${file}: UTF-8无效`);
  }
  assert.equal(data.docs.length,docs.size);
  assert.equal(data.readingAliases['docs/00-guide/backend-six-week-plan.md'].sections['第3周-缓存与并发控制'],'week-2');
});
check('学习路线只有一个正文和索引条目，进阶与独特练习仍可找到',()=>{
  const canonical='docs/00-guide/expanded-map-and-study-plan.md';
  const guide=data.docs.filter(d=>d.module==='guide');
  assert.deepEqual([...guide].map(d=>d.path),[canonical]);
  assert.equal(index.documents.filter(d=>d.category==='学习路线').length,1);
  assert.equal(fs.readdirSync(path.join(root,'docs/00-guide')).filter(p=>p.endsWith('.md')).length,1);
  const route=docs.get(canonical);
  for(const id of ['learning-main-language','six-week-plan','week-1','week-2','week-3','week-4','week-5','week-6','daily-practice','project-workflow','followup-route-agent','followup-route-java','followup-route-go','followup-route-storage','followup-route-practice','advanced-topics','resume-to-questions','cache-interview-ladder'])assert.ok(route.headings.some(h=>h.id===id),id);
  for(const q of ['RC/RR','位点提交','回源并发','Spark','LC395','ES 父子','KV'])assert.ok(route.source.includes(q),q);
  assert.equal((docs.get('docs/70-practice/algorithm-and-sql-plan.md').source.match(/^\d\. /gm)||[]).length,8);
  assert.equal(Object.keys(data.readingAliases).length,4);
  for(const [old,alias] of Object.entries(data.readingAliases)){
    assert.equal(alias.path,canonical);assert.ok(!docs.has(old));
    assert.ok(!index.documents.some(d=>d.relative_path===old));
    for(const section of [alias.section,...Object.values(alias.sections)])assert.ok(route.headings.some(h=>h.id===section),`${old}#${section}`);
  }
});
check('全部规范 Markdown 进入阅读层，不复制有相对链接的孤立 Markdown',()=>{
  const walk=dir=>fs.readdirSync(path.join(root,dir),{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(`${dir}/${e.name}`):[`${dir}/${e.name}`]);
  for(const file of ['docs','examples','coverage','errata','sources'].flatMap(walk).filter(p=>p.endsWith('.md')))assert.ok(docs.has(file),file);
  for(const file of walk('site/assets/repo'))assert.ok(!file.endsWith('.md'),`Markdown 应通过阅读路由打开，不能孤立复制：${file}`);
  for(const file of ['examples/hot100/README.md','coverage/README.md','coverage/VALIDATION.md']){
    assert.ok(docs.has(file),file);
    assert.ok(docs.get(file).html.includes('href="#/read/'),`${file} 的 Markdown 关联链接应转译为阅读路由`);
  }
});
check('全量原文 Markdown 相对链接扫描通过',()=>{
  const marked=new Marked();
  let scanned=0;
  for(const d of data.docs){
    marked.walkTokens(marked.lexer(d.source),token=>{
      if(!['link','image'].includes(token.type)||!token.href||/^[a-z][\w+.-]*:/i.test(token.href))return;
      const file=decodeURIComponent(token.href.split('#')[0].split('?')[0]);
      if(!file)return;
      const target=path.resolve(root,path.dirname(d.path),file);
      assert.ok(target.startsWith(root+path.sep),`${d.path}: 目标超出仓库 ${token.href}`);
      assert.ok(fs.existsSync(target),`${d.path}: 相对链接缺目标 ${token.href}`);
      scanned++;
    });
  }
  assert.ok(scanned>1000,`应扫描整个讲义而非小样本：${scanned}`);
  console.log(`  已扫描 ${scanned} 个相对链接。`);
});
check('每章锚点唯一且不含 undefined',()=>{
  for(const d of data.docs){const ids=[...d.html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,d.path);assert.ok(!ids.includes('undefined'),d.path);for(const h of d.headings)assert.ok(ids.includes(h.id),`${d.path}#${h.id}`);}
});
check('内部阅读链接及章内锚点有效',()=>{
  for(const d of data.docs){for(const m of d.html.matchAll(/href="#\/read\/([^"?]+)(?:\?section=([^"&]+))?"/g)){const target=docs.get(decodeURIComponent(m[1]));assert.ok(target,`${d.path} -> ${m[1]}`);if(m[2]){const id=decodeURIComponent(m[2]);assert.ok(target.headings.some(h=>h.id===id),`${d.path} -> ${target.path}#${id}`);}}}
});
check('关联源码与资源使用当前文件的自动副本',()=>{
  for(const d of data.docs){for(const m of d.html.matchAll(/href="assets\/repo\/([^"#]+)(?:#[^"]*)?"/g)){const file=decodeURIComponent(m[1]);assert.ok(!file.startsWith('../'));assert.ok(fs.readFileSync(path.join(site,'assets/repo',file)).equals(fs.readFileSync(path.join(root,file))),file);}}
});
check('Pages关联资源不使用被隐藏目录排除的路径',()=>{
  for(const d of data.docs){for(const m of d.html.matchAll(/href="assets\/repo\/([^"#]+)(?:#[^"]*)?"/g)){const file=decodeURIComponent(m[1]);assert.ok(!file.split('/').some(part=>part.startsWith('.')),`${d.path}: 隐藏路径应使用已核实的GitHub文件链接 ${file}`);}}
  const validation=docs.get('coverage/VALIDATION.md');
  assert.ok(validation.html.includes('href="https://github.com/minimoster/agent-backend-interview-handbook/blob/6dacaf1dd1f6f7bd5b71b8e74c017e9d5a91e833/.github/workflows/knowledge-checks.yml"'));
});
check('静态输出不执行原始脚本或危险链接',()=>{
  assert.ok(!dataText.includes('</script>'));
  for(const d of data.docs){assert.ok(!/<script\b|<iframe\b|<object\b|\bon\w+\s*=|href=["'](?:javascript|data):/i.test(d.html),d.path);assert.ok(d.sourceUrl.startsWith(data.repositoryUrl+'/blob/'));}
  const html=fs.readFileSync(path.join(site,'index.html'),'utf8');
  assert.ok(html.includes("connect-src 'none'"));
  for(const m of html.matchAll(/(?:src|href)="(assets\/[^"]+)"/g))assert.ok(fs.existsSync(path.join(site,m[1].split('?')[0])),m[1]);
});
check('中文全文搜索定位正文段落，而非只搜标题',()=>{
  const result=engine.query(new URLSearchParams({q:'极端哈希碰撞'})).results;
  assert.ok(result.some(r=>r.d.problemId===1&&r.section.id==='复杂度'));
  assert.ok(engine.query(new URLSearchParams({q:'线程池'})).results.some(r=>r.d.path.includes('concurrency-and-thread-pools')));
  assert.ok(engine.query(new URLSearchParams({q:'user_id'})).results.length>0,'代码中的下划线应保留可搜索');
});
check('题号与大小写/全角输入可定位精确章节',()=>{
  const first=engine.query(new URLSearchParams({q:'Ａ０１'})).results[0];
  assert.ok(first.d.questionIds.includes('A01'));assert.equal(first.section.id,'a01');
  assert.equal(engine.query(new URLSearchParams({q:'lc287'})).results[0].d.problemId,287);
  assert.equal(engine.query(new URLSearchParams({q:'两数之和'})).results[0].d.problemId,1);
});
check('多关键词以 AND 匹配，空搜索与无结果状态有界',()=>{
  const result=engine.query(new URLSearchParams({q:'库存 幂等'})).results;
  assert.ok(result.length>0);
  for(const r of result){const text=normalize(r.d.title+' '+r.d.sections.map(s=>s.heading+' '+s.text).join(' '));assert.ok(text.includes('库存')&&text.includes('幂等'));}
  assert.equal(engine.query(new URLSearchParams({q:'   '})).results.length,data.docs.length);
  assert.equal(engine.query(new URLSearchParams({q:'从未存在的搜索结果XYZ987'})).results.length,0);
});
check('Hot100 主题与官方难度筛选准确',()=>{
  const hash=engine.query(new URLSearchParams({module:'hot100',topic:'哈希'})).results;
  assert.equal(hash.length,3);assert.ok(hash.every(r=>r.d.category==='哈希'));
  for(const difficulty of ['EASY','MEDIUM','HARD']){const result=engine.query(new URLSearchParams({module:'hot100',difficulty})).results;assert.equal(result.length,manifest.problems.filter(p=>p.difficulty===difficulty).length);assert.ok(result.every(r=>r.d.difficulty===difficulty));}
  assert.equal(engine.query(new URLSearchParams({module:'java',difficulty:'HARD'})).results.length,0);
});
check('Carl资源保持361/100计数，15补充题作为独立资源条目',()=>{
  assert.equal(data.questionCount,461);assert.equal(data.questionCount-data.hot100Count,361);assert.equal(data.hot100Count,100);
  assert.equal(data.supplementaryCount,15);assert.equal(data.supplementaryResources.length,15);
  const hotIds=new Set(manifest.problems.map(p=>p.id));
  assert.equal(new Set(data.supplementaryResources.map(p=>p.resourceProblemId)).size,15);
  for(const r of data.supplementaryResources){assert.ok(!hotIds.has(r.resourceProblemId));assert.equal(r.kind,'external-resource');assert.equal(r.problemId,null);assert.ok(!r.code_path&&!r.python_path&&!r.html&&!r.source);assert.ok(docs.get(r.path).headings.some(h=>h.id===r.targetAnchor));assert.equal(r.sections[0].id,r.targetAnchor);}
});
check('15题逐项搜索、题号锚点、分类与官方难度筛选正确',()=>{
  const all=fullEngine.query(new URLSearchParams({module:'supplement'})).results;
  assert.equal(all.length,15);assert.ok(all.every(r=>r.d.kind==='external-resource'));
  assert.deepEqual(all.map(r=>r.d.resourceProblemId),carl.supplementary_index.problems.map(r=>r.id));
  for(const entry of carl.supplementary_index.problems){
    const result=fullEngine.query(new URLSearchParams({q:'LC'+entry.id})).results[0];
    assert.equal(result.d.resourceProblemId,entry.id);assert.equal(result.section.id,entry.article_anchor);assert.equal(result.d.difficulty,entry.difficulty);
    assert.ok(fullEngine.query(new URLSearchParams({module:'supplement',q:entry.title_zh})).results.some(r=>r.d.resourceProblemId===entry.id));
  }
  for(const topic of new Set(carl.supplementary_index.problems.map(r=>r.topic)))assert.equal(fullEngine.query(new URLSearchParams({module:'supplement',topic})).results.length,carl.supplementary_index.problems.filter(r=>r.topic===topic).length);
  for(const difficulty of ['EASY','MEDIUM','HARD'])assert.equal(fullEngine.query(new URLSearchParams({module:'supplement',difficulty})).results.length,carl.supplementary_index.problems.filter(r=>r.difficulty===difficulty).length);
  const bank='docs/85-algorithm-supplement/README.md';
  assert.equal(fullEngine.query(new URLSearchParams({view:'saved'}),{saved:[bank],done:[]}).results.length,1,'章级收藏不应复制成15份记录');
});
check('Carl入口的精确资源/相关视频分类与核查映射完全一致',()=>{
  for(const entry of carl.problems){
    const d=docs.get(entry.doc_path),c=d.carl;
    assert.ok(d.headings.some(h=>h.id===c.anchor));assert.equal(Boolean(c.explanation),entry.has_direct_explanation);assert.equal(Boolean(c.python),entry.has_direct_python_implementation);
    assert.deepEqual([...c.directVideos].map(v=>v.url),entry.direct_videos.map(v=>v.url));assert.deepEqual([...c.relatedVideos].map(v=>v.url),entry.related_videos.map(v=>v.url));
    assert.equal(c.author,'代码随想录（程序员Carl）');assert.equal(c.checkedDate,entry.checked_date);
  }
  const right=docs.get('docs/80-hot100/problems/0199-binary-tree-right-side-view.md').carl;
  assert.equal(right.directVideos.length,0);assert.ok(right.relatedVideos.length>0);
  const course=docs.get('docs/80-hot100/problems/0207-course-schedule.md').carl;
  assert.ok(course.explanation);assert.equal(course.python,null);assert.equal(course.directVideos.length,0);
});
check('收藏与已读筛选仅使用传入的本地状态',()=>{
  const p=data.docs[0].path;
  assert.equal(engine.query(new URLSearchParams({view:'saved'}),{saved:[p],done:[]}).results[0].d.path,p);
  assert.equal(engine.query(new URLSearchParams({view:'saved'}),{saved:[],done:[]}).results.length,0);
  assert.equal(engine.query(new URLSearchParams({view:'done'}),{saved:[],done:[p]}).results.length,1);
});
check('代码文本未因高亮丢失字符，解答和知识区可折叠',()=>{
  const d=data.docs.find(d=>d.problemId===1);
  const code=d.html.match(/<pre[^>]*><code>([\s\S]*?)<\/code><\/pre>/)?.[1].replace(/<[^>]*>/g,'').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');
  assert.equal(code,d.source.match(/```python\n([\s\S]*?)\n```/)[1]);
  assert.ok(d.html.includes('class="answer-section"'));
  assert.ok(docs.get('docs/10-agent/01-agent-loop-tools-and-state.md').html.includes('class="knowledge-section"'));
});
check('手机与无障碍规则存在（静态检查，不是实测）',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8'),app=fs.readFileSync(path.join(site,'assets/app.js'),'utf8');
  assert.ok(css.includes('@media(max-width:420px)'));
  assert.ok(css.includes('@media(max-width:720px)'));
  assert.ok(css.includes('overflow-x:auto'));
  assert.ok(css.includes('focus-visible'));
  assert.ok(css.includes('prefers-reduced-motion'));
  assert.ok(css.includes('font-size:clamp(23px,7vw,27px)'),'极窄屏标题应适当缩小，390px保持27px');
  assert.ok(css.includes('.hero-stats{flex-wrap:wrap}'),'额外补充题统计应可换行');
  assert.ok(app.includes('sidebar.inert=innerWidth<=960'));
  assert.ok(app.includes("e.key==='Escape'"));
  assert.ok(!/\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket/.test(app));
});
check('浅色 muted 普通文字与主要阅读背景达到 AA 4.5:1',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8');
  const light=css.match(/:root\{([^}]+)\}/)[1];
  const color=name=>light.match(new RegExp(`--${name}:(#[0-9a-f]{6});`,'i'))[1];
  for(const background of ['sidebar','bg','panel','paper','accent-soft']){
    const contrast=contrastRatio(color('muted'),color(background));
    assert.ok(contrast>=4.5,`muted / ${background}: ${contrast.toFixed(4)}:1`);
    if(background==='sidebar')console.log(`  浅色侧栏普通文字对比度 ${contrast.toFixed(4)}:1。`);
  }
});
check('明暗主题正文、导航、状态标签与代码小字主要配色达到 AA',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8');
  const definitions=[css.match(/:root\{([^}]+)\}/)[1],css.match(/html\[data-theme=dark\]\{([^}]+)\}/)[1]];
  const directColor=selector=>css.match(new RegExp(selector.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\{[^}]*?color:(#[0-9a-f]{6})','i'))[1];
  const assertAA=(fg,bg,label)=>assert.ok(contrastRatio(fg,bg)>=4.5,`${label}: ${contrastRatio(fg,bg).toFixed(4)}:1`);
  for(const [theme,definition] of definitions.entries()){
    const color=name=>definition.match(new RegExp(`--${name}:(#[0-9a-f]{6});`,'i'))[1];
    for(const fg of ['ink','text','muted','accent'])for(const bg of ['sidebar','bg','panel','paper','accent-soft'])assertAA(color(fg),color(bg),`${theme?'dark':'light'} ${fg}/${bg}`);
    assertAA(color('code-ink'),color('code-bg'),'code body');
    for(const selector of ['.code-toolbar','.copy-code','.code-comment','.code-string','.code-keyword','.code-number'])assertAA(directColor(selector),color('code-bg'),selector);
    for(const level of ['medium','hard'])assertAA(directColor(`${theme?'html[data-theme=dark] ':''}.badge.${level}`),color('paper'),`${theme?'dark':'light'} badge ${level}`);
  }
});
check('搜索占位符显式采用主题 muted 色，明暗背景均达到 AA',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8');
  const rule=css.match(/\.header-search input::placeholder\{([^}]+)\}/)?.[1]||'';
  assert.ok(rule.includes('color:var(--muted)'));
  assert.ok(rule.includes('opacity:1'));
  for(const definition of [css.match(/:root\{([^}]+)\}/)[1],css.match(/html\[data-theme=dark\]\{([^}]+)\}/)[1]]){
    const color=name=>definition.match(new RegExp(`--${name}:(#[0-9a-f]{6});`,'i'))[1];
    assert.ok(contrastRatio(color('muted'),color('panel'))>=4.5);
  }
});
check('知识修订可检索，36条Agent追问参考答案可折叠且题数独立',()=>{
  const expected=[['docs/10-agent/01-agent-loop-tools-and-state.md',8],['docs/10-agent/02-rag-retrieval-and-reranking.md',10],['docs/10-agent/03-memory-and-context.md',5],['docs/10-agent/04-streaming-and-reliable-execution.md',7],['docs/50-projects/public-repository-case-studies.md',6]];
  for(const [file,count] of expected){
    const doc=docs.get(file);
    assert.equal((doc.html.match(/class="answer-section"/g)||[]).length,count,file);
    assert.equal((doc.source.match(/\*\*验收点：\*\*/g)||[]).length,count,file);
  }
  const has=(q,file)=>engine.query(new URLSearchParams({q})).results.some(r=>r.d.path===file);
  assert.ok(has('fingerprint','docs/50-projects/data-engineering-agent-case.md'));
  assert.ok(has('子块全文字符串','docs/50-projects/public-repository-case-studies.md'));
  assert.ok(has('Last-Event-ID','docs/10-agent/04-streaming-and-reliable-execution.md'));
  assert.ok(docs.get('QUESTION_INDEX.md').source.includes('Agent补充 · 23题'));
  assert.equal(index.counts.interview_questions,361);
  assert.equal(data.hot100Count,100);
  assert.equal(data.supplementaryCount,15);
});
check('26张公开场景卡编号、搜索、原文、追问与既有题数独立',()=>{
  const scenes=JSON.parse(fs.readFileSync(path.join(root,'sources/public-interviews/scenario-map.json'),'utf8')).records;
  assert.equal(data.scenarioCount,26);assert.equal(data.publicSelfReportCount,17);
  assert.equal(data.docs.filter(d=>d.kind==='scenario').length,26);
  assert.equal(data.modules.find(m=>m.id==='scenarios').count,26);
  for(const scene of scenes){
    const doc=docs.get(scene.file);assert.equal(doc.scenarioCardId,scene.card_id);assert.deepEqual([...doc.questionIds],[scene.card_id]);
    const found=engine.query(new URLSearchParams({q:scene.card_id})).results[0];assert.equal(found.d.path,scene.file,scene.card_id);
    assert.ok(doc.html.includes('class="answer-section"'));assert.ok(doc.html.includes('class="knowledge-section"'));
  }
  assert.equal(engine.query(new URLSearchParams({q:'A01'})).results[0].d.scenarioCardId,null,'原讲义A01不应被SC-A01抢占');
  assert.equal(engine.query(new URLSearchParams({module:'scenarios',topic:'Agent应用'})).results.filter(r=>r.d.kind==='scenario').length,12);
  assert.equal(engine.query(new URLSearchParams({module:'scenarios',topic:'后端可靠性'})).results.filter(r=>r.d.kind==='scenario').length,14);
  assert.equal(data.questionCount,461);assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);
});
check('生产页面脚本非渲染启动：总览、搜索、阅读与禁用存储',()=>{
  // Minimal DOM stubs check runtime initialization only. They do not lay out or paint a page.
  function boot(hash,allowStorage=true,initialState={}){
    const nodes=new Map();
    const stub=()=>({innerHTML:'',textContent:'',value:'',hidden:true,dataset:{},listeners:{},style:{setProperty(){}},classList:{add(){},remove(){},contains(){return false;},toggle(){}},setAttribute(){},removeAttribute(){},getAttribute(){return '';},addEventListener(name,fn){this.listeners[name]=fn;},querySelectorAll(){return [];},contains(){return false;},focus(){this.focused=true;},scrollIntoView(){this.scrolled=true;},select(){}});
    const doc={getElementById(id){if(!nodes.has(id))nodes.set(id,stub());return nodes.get(id);},querySelector(selector){return this.getElementById(selector);},querySelectorAll(){return [];},addEventListener(){},documentElement:stub(),activeElement:null};
    const sandbox={window:{},document:doc,innerWidth:390,location:{hash},URLSearchParams,localStorage:{getItem(){if(!allowStorage)throw Error('disabled');return JSON.stringify(initialState);},setItem(key,value){if(!allowStorage)throw Error('disabled');sandbox.savedState=JSON.parse(value);}},history:{replaceState(a,b,hash){sandbox.location.hash=hash;}},setTimeout(){return 1;},clearTimeout(){},requestAnimationFrame(fn){fn();},getComputedStyle(){return {display:'block'};}};
    sandbox.window.matchMedia=()=>({matches:false});sandbox.window.scrollTo=()=>{};sandbox.window.addEventListener=()=>{};
    for(const match of html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g))vm.runInNewContext(fs.readFileSync(path.join(site,match[1]),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(dataText,sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/search.js'),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/app.js'),'utf8'),sandbox,{timeout:10000});
    return {html:nodes.get('main').innerHTML,title:doc.title,nodes,sandbox};
  }
  const canonical='docs/00-guide/expanded-map-and-study-plan.md';
  const aliases=Object.entries(data.readingAliases);
  for(const [old,alias] of aliases){
    assert.ok(!docs.has(old),old);
    for(const [original,expected] of [['',alias.section],['unknown-deleted-section',alias.section],...Object.entries(alias.sections)]){
      const legacy=boot(`#/read/${encodeURIComponent(old)}${original?'?section='+encodeURIComponent(original):''}`);
      const query=new URLSearchParams(legacy.sandbox.location.hash.split('?')[1]);
      assert.ok(legacy.sandbox.location.hash.startsWith('#/read/'+encodeURIComponent(canonical)),old);
      assert.equal(query.get('section'),expected,`${old}#${original}`);
      assert.ok(legacy.html.includes('学习路线：用一个项目串起 Agent 与后端'));
    }
  }
  for(const [old,section] of Object.entries(data.readingSectionAliases[canonical])){
    const legacy=boot(`#/read/${encodeURIComponent(canonical)}?section=${encodeURIComponent(old)}`);
    assert.equal(new URLSearchParams(legacy.sandbox.location.hash.split('?')[1]).get('section'),section);
    assert.ok(docs.get(canonical).headings.some(h=>h.id===section));
  }
  const migrated=boot('#/',true,{saved:[...aliases.map(([old])=>old),canonical],done:[...aliases.map(([old])=>old),canonical],lastPath:aliases[0][0]});
  assert.deepEqual([...migrated.sandbox.savedState.saved],[canonical]);
  assert.deepEqual([...migrated.sandbox.savedState.done],[canonical]);
  assert.equal(migrated.sandbox.savedState.lastPath,canonical);
  assert.equal(migrated.nodes.get('saved-count').textContent,1);
  assert.equal(migrated.nodes.get('done-count').textContent,1);
  assert.ok(migrated.html.includes('继续阅读'));
  assert.ok(boot('#/').html.includes('把知识连成一条主线'));
  assert.ok(boot('#/').html.includes('场景卡'));
  assert.equal(boot('#/').title,'AI Agent 与后端开发学习手册');
  assert.ok(boot('#/').html.includes('从 Agent 应用到后端工程，系统学习核心知识、项目实践与面试方法。'));
  assert.ok(html.includes('aria-label="AI Agent 与后端开发学习手册首页"'));
  assert.ok(html.includes('class="brand-name-ending">学习手册</span>'));
  assert.ok(fs.readFileSync(path.join(site,'assets/style.css'),'utf8').includes('.brand-name-ending{white-space:nowrap}'));
  assert.ok(!html.includes('工程学习手册'));
  assert.ok(boot('#/library?q=SC-A01').title.endsWith(' · AI Agent 与后端开发学习手册'));
  assert.ok(boot('#/library?q=SC-A01').html.includes('SC-A01'));
  assert.ok(boot('#/read/docs%2F90-public-interview-scenarios%2Fsc-a01.md').html.includes('练习问题'));
  assert.ok(boot('#/read/docs%2F90-public-interview-scenarios%2Fsc-b13.md',false).html.includes('TCP read边界'));
  const searched=boot('#/library?q=A01');assert.ok(searched.html.includes('A01'));assert.ok(searched.html.includes('section=a01'));
  assert.ok(boot('#/library?q=绝不存在987XYZ').html.includes('暂时没有匹配'));
  assert.ok(boot('#/read/docs%2F80-hot100%2Fproblems%2F0001-two-sum.md').html.includes('两数之和'));
  assert.ok(boot('#/library?view=saved',false).html.includes('未允许本地存储'));
  const supplement=boot('#/library?module=supplement').html;
  assert.equal((supplement.match(/class="result-item"/g)||[]).length,15);
  assert.ok(supplement.includes('section=problem-77'));assert.ok(supplement.includes('外部资源题库'));
  const carlReader=boot('#/read/docs%2F80-hot100%2Fproblems%2F0001-two-sum.md').html;
  assert.ok(carlReader.includes('本题精确讲解'));assert.ok(carlReader.includes('本题 Python 区'));assert.ok(carlReader.includes('代码随想录（程序员Carl）'));
  const relatedReader=boot('#/read/docs%2F80-hot100%2Fproblems%2F0199-binary-tree-right-side-view.md').html;
  assert.ok(relatedReader.includes('相关题迁移，非本题配套'));assert.ok(relatedReader.includes('本题直接视频：本次未找到'));
  const javaReader=boot('#/read/docs%2F20-java%2F16-executor-failure-followups.md').html;
  assert.ok(javaReader.includes('href="assets/repo/examples/interview_followups/ExecutorFailureLab.java" download="ExecutorFailureLab.java"'));
  assert.ok(/<a class="source-fallback"[^>]+href="https:\/\/github\.com\/[^>]+>GitHub ↗<\/a>/.test(javaReader),'保留独立 GitHub 查看链接');
  assert.ok(!/<a[^>]+href="https:\/\/github\.com\/[^>]+\bdownload=/.test(javaReader),'不能对外部 GitHub 链接强制下载');
  const designReader=boot('#/read/docs%2F40-backend%2F42-system-design-debugging-clinic.md').html;
  assert.ok(designReader.includes('href="assets/repo/examples/interview_followups/ExecutorFailureLab.java" download="ExecutorFailureLab.java"'),'设计章的同一源码入口');
  const goReader=boot('#/read/examples%2Fgo%2Ffollowup_lifecycle%2FREADME.md').html;
  for(const file of ['go.mod','pool.go','pool_test.go']){
    assert.ok(goReader.includes(`href="assets/repo/examples/go/followup_lifecycle/${file}" download="${file}"`),file);
    assert.ok(goReader.includes(`<a href="assets/repo/examples/go/followup_lifecycle/${file}">${file}</a>`),'普通源码浏览链接保持原样');
  }
  const storageReader=boot('#/read/docs%2F40-backend%2F41-storage-recovery-followups.md').html;
  for(const file of ['storage_lab.py','test_storage_lab.py'])assert.ok(storageReader.includes(`href="assets/repo/examples/interview_followups/${file}" download="${file}"`),file);
  const readingHash='#/read/docs%2F80-hot100%2Fproblems%2F0146-lru-cache.md';
  const reading=boot(readingHash);
  let prevented=false;
  reading.nodes.get('.skip-link').listeners.click({preventDefault(){prevented=true;}});
  assert.ok(prevented,'跳到主要内容应阻止替换hash路由');
  assert.equal(reading.sandbox.location.hash,readingHash);
  assert.ok(reading.nodes.get('main').focused&&reading.nodes.get('main').scrolled);
  assert.ok(reading.nodes.get('main').innerHTML.includes('LRU 缓存'));
});
check('原创Agent与Python专题保持既有题数和独立模块',()=>{
  const chapters=[
    'docs/10-agent/25-agent-evaluation-and-routing.md',
    'docs/10-agent/26-agent-production-design-lab.md',
    'docs/10-agent/27-practical-agent-scenarios.md',
    'docs/10-agent/28-frontier-and-engineering-decisions.md',
    'docs/10-agent/29-framework-selection-and-integration.md',
    'docs/10-agent/30-rag-data-and-chunking-lab.md',
    'docs/10-agent/31-tool-mcp-and-skill-contracts.md',
    'docs/40-backend/40-python-fastapi-lab.md',
    'docs/70-practice/ai-coding-exercises.md',
    'docs/90-interview/01-evidence-based-interview-preparation.md'
  ];
  for(const file of chapters){assert.ok(docs.has(file),file);assert.equal(docs.get(file).questionIds.length,0,file);assert.equal(index.documents.filter(d=>d.relative_path===file).length,1,file);}
  assert.equal(docs.get(chapters[9]).module,'preparation');
  assert.equal(data.questionCount,461);assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);assert.equal(data.scenarioCount,26);
  assert.ok(docs.get('docs/10-agent/24-inference-and-serving-boundaries.md').headings.some(h=>h.id==='kv-memory-budget'));
  assert.ok(!docs.has('chapters/kv_cache_supplement.md'),'KV内容合并到既有章');
});
check('新专题正文检索能定位真实锚点且现代协议保持未测',()=>{
  const expectations=[
    ['校准阈值','docs/10-agent/25-agent-evaluation-and-routing.md'],
    ['MMR','docs/10-agent/30-rag-data-and-chunking-lab.md'],
    ['依赖缓存','docs/40-backend/40-python-fastapi-lab.md'],
    ['ROUND_HALF_UP','docs/70-practice/ai-coding-exercises.md']
  ];
  for(const [q,file] of expectations){const result=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===file);assert.ok(result,`${q}: ${file}`);assert.ok(result.section.id);}
  const modern=docs.get('docs/10-agent/31-tool-mcp-and-skill-contracts.md').source;
  assert.ok(modern.includes('未运行2026-07-28互通或迁移测试'));
  assert.ok(modern.includes('2025-11-25'));
  assert.ok(docs.get('coverage/AGENT_LABS_VALIDATION.md').source.includes('合计94项'));
});


check('Transformer原创先修导航、形状搜索与源码保持独立口径',()=>{
  const chapterPath='docs/10-agent/05-transformer-prerequisite.md';
  const chapter=docs.get(chapterPath);
  assert.ok(chapter);
  assert.equal(chapter.source,fs.readFileSync(path.join(root,chapterPath),'utf8'));
  assert.equal(data.questionCount-data.hot100Count,361);
  assert.equal(data.hot100Count,100);
  assert.equal(data.supplementaryCount,15);
  assert.equal(data.scenarioCount,26);
  const entry=index.documents.find(d=>d.relative_path===chapterPath);
  assert.ok(entry);assert.deepEqual(entry.question_ids,[]);
  assert.ok(!index.items.some(i=>(i.relative_path||i.path)===chapterPath));
  for(const id of ['transformer-qkv','transformer-scaled-attention','transformer-mask','transformer-multihead','transformer-shapes','transformer-ffn','transformer-residual-norm','transformer-interview'])assert.ok(chapter.headings.some(h=>h.id===id),id);
  for(const q of ['总体方差','Post-LN','W_O','d_model','Q K V']){const r=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===chapterPath);assert.ok(r,q);assert.ok(chapter.headings.some(h=>h.id===r.section.id),q);}
  for(const file of ['attention_lab.py','test_attention_lab.py']){const relative=`examples/transformer_prerequisite/${file}`;assert.ok(chapter.html.includes(`href="assets/repo/${relative}"`));assert.ok(fs.readFileSync(path.join(site,'assets/repo',relative)).equals(fs.readFileSync(path.join(root,relative))));}
  for(const file of ['README.md','docs/10-agent/README.md','docs/10-agent/00-reading-guide.md'])assert.ok(docs.get(file).html.includes(encodeURIComponent(chapterPath)),file);
  for(const file of ['sources/transformer-prerequisite-references.md','coverage/TRANSFORMER_PREREQUISITE_VALIDATION.md','examples/transformer_prerequisite/README.md'])assert.ok(docs.has(file),file);
});


check('面经六篇追问与一路线保持既有编号并有唯一真实锚点',()=>{
  const paths=[
    'docs/00-guide/expanded-map-and-study-plan.md',
    'docs/10-agent/32-a2a-task-lifecycle-lab.md',
    'docs/10-agent/33-tool-stream-assembly-lab.md',
    'docs/20-java/16-executor-failure-followups.md',
    'docs/30-go/07-concurrency-failure-followups.md',
    'docs/40-backend/41-storage-recovery-followups.md',
    'docs/40-backend/42-system-design-debugging-clinic.md'
  ];
  assert.equal(data.questionCount,461);assert.equal(data.questionCount-data.hot100Count,361);
  assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);assert.equal(data.scenarioCount,26);assert.equal(data.publicSelfReportCount,17);
  for(const file of paths){
    const d=docs.get(file);assert.ok(d,file);assert.equal(d.questionIds.length,0);
    assert.equal(index.documents.filter(entry=>entry.relative_path===file).length,1,file);
    assert.ok(!index.items.some(item=>(item.relative_path||item.path)===file),file);
    const anchors=[...d.source.matchAll(/<a id="([^"]+)"><\/a>/g)].map(match=>match[1]);
    assert.ok(anchors.length>=5,file);assert.equal(new Set(anchors).size,anchors.length,file);
    for(const id of anchors)assert.equal(d.headings.filter(h=>h.id===id).length,1,`${file}#${id}`);
  }
  for(const file of ['sources/interview-followups/README.md','sources/agent-protocol-references.md','coverage/INTERVIEW_FOLLOWUPS_VALIDATION.md','examples/interview_followups/README.md','examples/go/followup_lifecycle/README.md'])assert.ok(docs.has(file),file);
  assert.ok(docs.get('README.md').html.includes(encodeURIComponent(paths[0])));
  for(const [file,target] of [['docs/10-agent/README.md',paths[1]],['docs/10-agent/README.md',paths[2]],['docs/20-java/README.md',paths[3]],['docs/30-go/README.md',paths[4]],['docs/40-backend/README.md',paths[5]],['docs/40-backend/README.md',paths[6]]])assert.ok(docs.get(file).html.includes(encodeURIComponent(target)),`${file}: ${target}`);
});
check('新追问正文搜索、源码下载及模型边界一致',()=>{
  for(const [q,file] of [
    ['SubscribeToTask','docs/10-agent/32-a2a-task-lifecycle-lab.md'],
    ['partial_json','docs/10-agent/33-tool-stream-assembly-lab.md'],
    ['orTimeout','docs/20-java/16-executor-failure-followups.md'],
    ['回调不合作','docs/30-go/07-concurrency-failure-followups.md'],
    ['nextOffsets','docs/40-backend/41-storage-recovery-followups.md'],
    ['灰度切读','docs/40-backend/42-system-design-debugging-clinic.md']
  ]){const result=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===file);assert.ok(result,`${q}: ${file}`);assert.ok(docs.get(file).headings.some(h=>h.id===result.section.id),q);}
  for(const relative of ['examples/interview_followups/ExecutorFailureLab.java','examples/interview_followups/storage_lab.py','examples/interview_followups/test_storage_lab.py','examples/interview_followups/agent_protocol_lab.py','examples/interview_followups/test_agent_protocol_lab.py','examples/go/followup_lifecycle/go.mod','examples/go/followup_lifecycle/pool.go','examples/go/followup_lifecycle/pool_test.go']){
    assert.ok(fs.readFileSync(path.join(site,'assets/repo',relative)).equals(fs.readFileSync(path.join(root,relative))),relative);
  }
  assert.ok(docs.get('coverage/INTERVIEW_FOLLOWUPS_VALIDATION.md').source.includes('本地未执行'));
  assert.ok(docs.get('docs/40-backend/41-storage-recovery-followups.md').source.includes('不保证'));
  assert.ok(docs.get('sources/interview-followups/README.md').source.includes('不计为原始候选人自报'));
});

check('显式源码下载控件不拆行且样式使用独立缓存版本',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8');
  assert.ok(css.includes('.reader-content .resource-download{display:inline-block;white-space:nowrap}'));
  assert.ok(html.includes('href="assets/style.css?v=source-download-nowrap-20261011"'));
});

check('虾皮Agent补充保留34个唯一题号、六栏目与独立计数',()=>{
  const file='docs/10-agent/34-shopee-agent-interview-playbook.md';
  const d=docs.get(file);
  const mapping=JSON.parse(fs.readFileSync(path.join(root,'sources/shopee-agent-question-map.json'),'utf8'));
  assert.ok(d,file);
  assert.equal(mapping.unique_question_count,34);
  assert.equal(mapping.records.length,34);
  assert.equal(new Set(mapping.records.map(r=>r.id)).size,34);
  assert.deepEqual(mapping.records.map(r=>[r.round,r.original_number]),[1,2].flatMap(round=>Array.from({length:17},(_,i)=>[round,i+1])));
  assert.equal(d.questionIds.length,34);
  assert.equal(data.questionCount,461);
  assert.equal(data.hot100Count,100);
  assert.equal(data.scenarioCount,26);
  assert.equal(data.publicSelfReportCount,17);
  assert.equal(data.supplementaryCount,15);
  for(const r of mapping.records){
    assert.equal(r.path,file);
    assert.ok(d.headings.some(h=>h.id===r.anchor&&h.text.includes(r.id)),r.id);
    const section=d.sections.find(s=>s.id===r.anchor);
    assert.ok(section,r.id);
    for(const label of ['新手概念','面试口述','落地设计','指标与失败边界','追问与误区','延伸阅读'])assert.ok(section.text.includes(label),`${r.id}: ${label}`);
  }
  assert.ok(!/libfile_|file_00000000|IMG_276[1-4]|oai-library:/.test(d.source));
  assert.ok(d.source.includes('示例指标为教学设定'));
});
check('虾皮Agent新题号与新增二面正文可搜索，导航相互连接',()=>{
  const file='docs/10-agent/34-shopee-agent-interview-playbook.md';
  for(const q of ['SP-R1-01','SP-R1-17','SP-R2-07','SP-R2-17','说话人分离','缓存读token']){
    const result=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===file);
    assert.ok(result,`${q} 未命中新章`);
    assert.ok(docs.get(file).headings.some(h=>h.id===result.section.id),q);
  }
  for(const p of ['README.md','QUESTION_INDEX.md','docs/10-agent/README.md','docs/10-agent/00-reading-guide.md','docs/60-interviews/README.md','docs/60-interviews/agent.md'])assert.ok(docs.get(p).html.includes(encodeURIComponent(file)),p);
  assert.ok(docs.has('sources/shopee-agent-interview-supplement.md'));
  assert.ok(docs.has('coverage/SHOPEE_AGENT_VALIDATION.md'));
});

console.log(`\n${checks} 组非渲染检查通过。实际浏览器、屏幕尺寸与辅助技术测试需另行进行。`);
