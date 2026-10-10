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
check('静态输出不执行原始脚本或危险链接',()=>{
  assert.ok(!dataText.includes('</script>'));
  for(const d of data.docs){assert.ok(!/<script\b|<iframe\b|<object\b|\bon\w+\s*=|href=["'](?:javascript|data):/i.test(d.html),d.path);assert.ok(d.sourceUrl.startsWith(data.repositoryUrl+'/blob/'));}
  const html=fs.readFileSync(path.join(site,'index.html'),'utf8');
  assert.ok(html.includes("connect-src 'none'"));
  for(const m of html.matchAll(/(?:src|href)="(assets\/[^"]+)"/g))assert.ok(fs.existsSync(path.join(site,m[1])),m[1]);
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
  function boot(hash,allowStorage=true){
    const nodes=new Map();
    const stub=()=>({innerHTML:'',textContent:'',value:'',hidden:true,dataset:{},listeners:{},style:{setProperty(){}},classList:{add(){},remove(){},contains(){return false;},toggle(){}},setAttribute(){},removeAttribute(){},getAttribute(){return '';},addEventListener(name,fn){this.listeners[name]=fn;},querySelectorAll(){return [];},contains(){return false;},focus(){this.focused=true;},scrollIntoView(){this.scrolled=true;},select(){}});
    const doc={getElementById(id){if(!nodes.has(id))nodes.set(id,stub());return nodes.get(id);},querySelector(selector){return this.getElementById(selector);},querySelectorAll(){return [];},addEventListener(){},documentElement:stub(),activeElement:null};
    const sandbox={window:{},document:doc,innerWidth:390,location:{hash},URLSearchParams,localStorage:{getItem(){if(!allowStorage)throw Error('disabled');return null;},setItem(){if(!allowStorage)throw Error('disabled');}},history:{replaceState(){}},setTimeout(){return 1;},clearTimeout(){},requestAnimationFrame(fn){fn();},getComputedStyle(){return {display:'block'};}};
    sandbox.window.matchMedia=()=>({matches:false});sandbox.window.scrollTo=()=>{};sandbox.window.addEventListener=()=>{};
    for(const match of html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g))vm.runInNewContext(fs.readFileSync(path.join(site,match[1]),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(dataText,sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/search.js'),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/app.js'),'utf8'),sandbox,{timeout:10000});
    return {html:nodes.get('main').innerHTML,title:doc.title,nodes,sandbox};
  }
  assert.ok(boot('#/').html.includes('把知识连成一条主线'));
  assert.ok(boot('#/').html.includes('原创场景卡'));
  assert.equal(boot('#/').title,'AI Agent 与后端开发学习手册');
  assert.ok(boot('#/').html.includes('从 Agent 应用到后端工程，系统学习核心知识、项目实践与面试方法。'));
  assert.ok(html.includes('class="brand-name">AI Agent 与后端开发学习手册'));
  assert.ok(!html.includes('工程学习手册'));
  assert.ok(boot('#/library?q=SC-A01').title.endsWith(' · AI Agent 与后端开发学习手册'));
  assert.ok(boot('#/library?q=SC-A01').html.includes('SC-A01'));
  assert.ok(boot('#/read/docs%2F90-public-interview-scenarios%2Fsc-a01.md').html.includes('独立原创场景卡'));
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
  const readingHash='#/read/docs%2F80-hot100%2Fproblems%2F0146-lru-cache.md';
  const reading=boot(readingHash);
  let prevented=false;
  reading.nodes.get('.skip-link').listeners.click({preventDefault(){prevented=true;}});
  assert.ok(prevented,'跳到主要内容应阻止替换hash路由');
  assert.equal(reading.sandbox.location.hash,readingHash);
  assert.ok(reading.nodes.get('main').focused&&reading.nodes.get('main').scrolled);
  assert.ok(reading.nodes.get('main').innerHTML.includes('LRU 缓存'));
});
console.log(`\n${checks} 组非渲染检查通过。实际浏览器、屏幕尺寸与辅助技术测试需另行进行。`);
