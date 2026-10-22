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
import {isReadingDocument,isTeachingResource,readingMarkdown} from './reading-policy.mjs';

const site=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(site);
execFileSync(process.execPath,[path.join(site,'build.mjs'),'--check'],{stdio:'inherit'});
const context={window:{}};
const dataText=fs.readFileSync(path.join(site,'assets/data.js'),'utf8');
const html=fs.readFileSync(path.join(site,'index.html'),'utf8');
for(const match of html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g))vm.runInNewContext(fs.readFileSync(path.join(site,match[1]),'utf8'),context,{timeout:10000});
vm.runInNewContext(dataText,context,{timeout:10000});
const publishedData=context.window.STUDY_DATA;
// Local-only fixtures support source/code comparisons. They are deliberately
// overlaid here, never serialized by the public build or read by the app.
const data={...publishedData,docs:publishedData.docs.map(doc=>({...doc,source:readingMarkdown(fs.readFileSync(path.join(root,doc.path),'utf8'),doc.path)}))};
const docs=new Map(data.docs.map(d=>[d.path,d]));
const index=JSON.parse(fs.readFileSync(path.join(root,'content-index.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8'));
const require=createRequire(import.meta.url);
const {create,normalize}=require('./assets/search.js');
const engine=create(data.docs);
const fullEngine=create([...data.docs,...(data.supplementaryResources||[])]);
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/reading-catalog.json'),'utf8'));
const supplementary=catalog.supplementaryProblems;
const walk=dir=>fs.readdirSync(path.join(root,dir),{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(`${dir}/${e.name}`):[`${dir}/${e.name}`]);
let checks=0;
const check=(name,fn)=>{fn();checks++;console.log(`PASS ${name}`);};
check('阅读界面只保留题目、解析、答案与必要源码入口',()=>{
  const app=fs.readFileSync(path.join(site,'assets/app.js'),'utf8');
  for(const phrase of ['代码随想录','程序员Carl','carlCard','source-view','GitHub 原文','来源与版本见正文','查看版本与来源','外部资源题库','external-resource','resource-bank'])assert.ok(!app.includes(phrase),phrase);
  assert.ok(app.includes('sourceDownloads'));
  assert.ok(!data.modules.some(m=>m.id==='reference'));
  assert.equal(data.modules.find(m=>m.id==='examples').label,'代码示例');
  assert.ok(!Object.hasOwn(data,'publicSelfReportCount'));
});
check('发布边界只接收教学文档和必要代码资源',()=>{
  for(const file of ['README.md','QUESTION_INDEX.md','docs/10-agent/README.md','docs/80-hot100/problems/0001-two-sum.md','examples/hot100/README.md'])assert.ok(isReadingDocument(file),file);
  for(const file of ['sources/README.md','coverage/README.md','errata/README.md','VERSIONS.md','CONTRIBUTING.md','site/README.md','docs/10-agent/SOURCES.md','docs/10-agent/VALIDATION.md','docs/10-agent/TESTING.md'])assert.ok(!isReadingDocument(file),file);
  for(const file of ['examples/hot100/p0001_two_sum.py','examples/interview_followups/ExecutorFailureLab.java','examples/go/followup_lifecycle/go.mod','examples/go/followup_lifecycle/pool.go','examples/sql/practice.sql','tests/test_example.py','examples/requirements.txt','examples/public_interview_scenarios/evaluation_design_template.json'])assert.ok(isTeachingResource(file),file);
  for(const file of ['sources/catalog.json','coverage/VALIDATION.md','site/build.mjs','content-index.json','examples/check_carl_resources.py','tests/validate_sources.py','examples/README.md'])assert.ok(!isTeachingResource(file),file);
});
check('阅读清洗移除资料元数据但保留技术版本、教学链接与代码',()=>{
  const sample=['# 教学示例','协议版本 2025-11-25；实现必须校验状态。','请求端点 `https://api.example.com/v1/responses?stream=true` 与 ``https://api.example.com/v1/chat/completions`` 必须逐字保留。','内联代码 `[调试示例](https://example.com/code-url)` 不应当作资料链接剥除。','作者：不应公开的资料作者','[文章](https://example.com/article) 与 [课程](https://example.com/video)','[教学章节](10-agent/README.md) · [验证](../coverage/VALIDATION.md) · [源数据](../sources/catalog.json)','[实现](../examples/demo.py)','[固定项目实现](https://github.com/example/project/blob/0123456789abcdef0123456789abcdef01234567/src/main.go#L1)','```python','# 来源不是代码中的元数据','print("https://example.com/kept-in-code")','```','## 来源','来源记录不应公开','### 细项','仍是来源记录','## 解答','保留这个教学答案。'].join('\n');
  const clean=readingMarkdown(sample,'docs/example.md');
  assert.ok(clean.includes('协议版本 2025-11-25'));
  assert.ok(clean.includes('`https://api.example.com/v1/responses?stream=true`'));
  assert.ok(clean.includes('``https://api.example.com/v1/chat/completions``'));
  assert.ok(clean.includes('`[调试示例](https://example.com/code-url)`'));
  assert.ok(clean.includes('[教学章节](10-agent/README.md)'));
  assert.ok(clean.includes('[实现](../examples/demo.py)'));
  assert.ok(clean.includes('[固定项目实现](https://github.com/example/project/blob/0123456789abcdef0123456789abcdef01234567/src/main.go#L1)'));
  assert.ok(clean.includes('# 来源不是代码中的元数据\nprint("https://example.com/kept-in-code")'));
  assert.ok(clean.includes('## 解答\n保留这个教学答案。'));
  for(const text of ['不应公开的资料作者','https://example.com/article','https://example.com/video','coverage/VALIDATION.md','sources/catalog.json','来源记录不应公开','仍是来源记录'])assert.ok(!clean.includes(text),text);
});
check('紧邻列表和表格的稳定锚点仍作为独立区块解析',()=>{
  const source='# 示例\n- 先做练习\n<a id="after-list"></a>\n## 列表之后\n| 项 | 值 |\n|---|---|\n| a | b |\n<a id="after-table"></a>\n## 表格之后\n回答。';
  const cleaned=readingMarkdown(source,'docs/example.md');
  const tokens=new Marked().lexer(cleaned);
  for(const id of ['after-list','after-table'])assert.ok(tokens.some(t=>t.raw.trim()===`<a id="${id}"></a>`),id);
  assert.deepEqual(tokens.filter(t=>t.type==='heading').map(t=>t.text),['示例','列表之后','表格之后']);
});
const relativeLuminance=hex=>{
  const channel=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(c=>c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4);
  return channel[0]*0.2126+channel[1]*0.7152+channel[2]*0.0722;
};
const contrastRatio=(foreground,background)=>{
  const a=relativeLuminance(foreground),b=relativeLuminance(background);
  return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
};

check('所有索引项与 Hot100 100 题均有阅读文档',()=>{
  assert.equal(data.questionCount,index.items.length);
  assert.equal(data.hot100Count,manifest.problems.length);
  assert.equal(data.docs.filter(d=>d.problemId).length,100);
  for(const item of index.items){const d=docs.get(item.relative_path||item.path);assert.ok(d,`${item.id} 路径缺失`);if(item.anchor)assert.ok(d.headings.some(h=>h.id===item.anchor),`${item.id} 锚点缺失：${item.anchor}`);}
});
check('阅读产物逐篇使用当前教学 Markdown，不暴露原文与来源字段',()=>{
  for(const d of data.docs){
    assert.equal(d.source,readingMarkdown(fs.readFileSync(path.join(root,d.path),'utf8'),d.path),d.path);
    const published=publishedData.docs.find(doc=>doc.path===d.path);
    for(const field of ['source','rawMarkdown','sourceUrl','attribution','author','checkedDate'])assert.ok(!Object.hasOwn(published,field),`${d.path}: ${field}`);
    assert.ok(!Object.hasOwn(d,'carl'),d.path);
  }
});
check('公开数据无Markdown回看字段或出处链接，下载不依赖远端fallback',()=>{
  for(const field of ['repositoryUrl','repository_url','sourceUrl','attribution','author','checkedDate'])assert.ok(!Object.hasOwn(publishedData,field),field);
  const forbidden=new Set(['source','rawMarkdown','rawSource','markdown','sourceUrl','attribution','author','checkedDate','repositoryUrl']);
  const inspect=(value,location)=>{
    if(!value||typeof value!=='object')return;
    for(const [key,child] of Object.entries(value)){
      assert.ok(!forbidden.has(key),`${location}.${key}`);
      inspect(child,`${location}.${key}`);
    }
  };
  inspect(publishedData,'public');
  for(const doc of publishedData.docs){
    assert.ok(!doc.html.includes('source-fallback'),doc.path);
    assert.ok(!doc.html.includes('github.com/minimoster/agent-backend-interview-handbook/blob/'),doc.path);
  }
  const builder=fs.readFileSync(path.join(site,'build.mjs'),'utf8');
  assert.ok(!builder.includes('const sourceUrl'));
  assert.ok(!builder.includes('source-fallback'));
});
check('小分片可逐个审阅并完整还原阅读数据',()=>{
  const scripts=[...html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g)].map(m=>m[1]);
  assert.ok(scripts.length>50,'分片应覆盖整本教学内容，不以旧rawMarkdown重复副本扩充体积');
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
check('教学 Markdown 完整注册，来源、版本与验证日志不进入阅读或下载',()=>{
  const expected=[...['docs','examples'].flatMap(walk),'README.md','QUESTION_INDEX.md'].filter(isReadingDocument).sort();
  assert.deepEqual([...docs.keys()].sort(),expected);
  for(const d of data.docs)assert.ok(isReadingDocument(d.path),d.path);
  for(const file of ['coverage/README.md','coverage/VALIDATION.md','errata/README.md','sources/README.md','VERSIONS.md','CONTRIBUTING.md','site/README.md','docs/10-agent/SOURCES.md'])assert.ok(!docs.has(file),file);
  for(const file of walk('site/assets/repo')){
    const target=file.slice('site/assets/repo/'.length);
    assert.ok(isTeachingResource(target),`只应镜像教学资源：${target}`);
    assert.ok(!file.endsWith('.md'),`Markdown 应通过阅读路由打开：${file}`);
  }
  const example=docs.get('examples/hot100/README.md');
  assert.ok(example);
  assert.ok(example.html.includes('href="#/read/'),'代码示例 Markdown 的教学链接应转译为阅读路由');
});
check('全量教学 Markdown 相对链接扫描通过',()=>{
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
      const relative=path.relative(root,target).split(path.sep).join('/');
      assert.ok(isReadingDocument(relative)||isTeachingResource(relative),`${d.path}: 不应关联非教学资料 ${token.href}`);
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
  for(const d of data.docs)assert.ok(!/href="(?:assets\/repo\/|#\/read\/)(?:sources|coverage|errata)(?:\/|%2F)/i.test(d.html),d.path);
});
check('静态输出不执行原始脚本或危险链接',()=>{
  assert.ok(!dataText.includes('</script>'));
  for(const d of data.docs)assert.ok(!/<script\b|<iframe\b|<object\b|\bon\w+\s*=|href=["'](?:javascript|data):/i.test(d.html),d.path);
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
check('364加100的主线计数准确，15补充题作为独立练习条目',()=>{
  assert.equal(data.questionCount,464);assert.equal(data.questionCount-data.hot100Count,364);assert.equal(data.hot100Count,100);
  assert.equal(data.supplementaryCount,15);assert.equal(data.supplementaryResources.length,15);
  const hotIds=new Set(manifest.problems.map(p=>p.id));
  assert.equal(new Set(data.supplementaryResources.map(p=>p.resourceProblemId)).size,15);
  for(const r of data.supplementaryResources){assert.ok(!hotIds.has(r.resourceProblemId));assert.equal(r.kind,'exercise');assert.equal(r.problemId,null);assert.ok(!r.code_path&&!r.python_path&&!r.html&&!r.source);assert.ok(docs.get(r.path).headings.some(h=>h.id===r.targetAnchor));assert.equal(r.sections[0].id,r.targetAnchor);}
});
check('15题逐项搜索、题号锚点、分类与官方难度筛选正确',()=>{
  const all=fullEngine.query(new URLSearchParams({module:'supplement'})).results;
  assert.equal(all.length,15);assert.ok(all.every(r=>r.d.kind==='exercise'));
  assert.deepEqual(all.map(r=>r.d.resourceProblemId),supplementary.map(r=>r.id));
  for(const entry of supplementary){
    const result=fullEngine.query(new URLSearchParams({q:'LC'+entry.id})).results[0];
    assert.equal(result.d.resourceProblemId,entry.id);assert.equal(result.section.id,entry.article_anchor);assert.equal(result.d.difficulty,entry.difficulty);
    assert.ok(fullEngine.query(new URLSearchParams({module:'supplement',q:entry.title_zh})).results.some(r=>r.d.resourceProblemId===entry.id));
  }
  for(const topic of new Set(supplementary.map(r=>r.topic)))assert.equal(fullEngine.query(new URLSearchParams({module:'supplement',topic})).results.length,supplementary.filter(r=>r.topic===topic).length);
  for(const difficulty of ['EASY','MEDIUM','HARD'])assert.equal(fullEngine.query(new URLSearchParams({module:'supplement',difficulty})).results.length,supplementary.filter(r=>r.difficulty===difficulty).length);
  const bank='docs/85-algorithm-supplement/README.md';
  assert.equal(fullEngine.query(new URLSearchParams({view:'saved'}),{saved:[bank],done:[]}).results.length,1,'章级收藏不应复制成15份记录');
});
check('补充练习保持中性教学数据，不带作者、来源或外部资源映射',()=>{
  assert.equal(catalog.schemaVersion,'1.0');
  assert.equal(supplementary.length,15);
  assert.equal(docs.get('docs/85-algorithm-supplement/README.md').kind,'exercise-bank');
  for(const entry of supplementary){
    assert.deepEqual(Object.keys(entry).sort(),['id','title_zh','topic','difficulty','doc_path','article_anchor','supplementary_order','original_review_prompt'].sort());
    assert.ok(entry.original_review_prompt.length>10);
    const resource=data.supplementaryResources.find(r=>r.resourceProblemId===entry.id);
    assert.ok(resource);
    assert.equal(resource.path,entry.doc_path);
    assert.equal(resource.targetAnchor,entry.article_anchor);
    assert.ok(!Object.hasOwn(resource,'carl')&&!Object.hasOwn(resource,'sourceUrl'));
    const teaching=resource.sections.map(s=>s.text).join('\n');
    for(const label of ['题目与接口合同','解析与不变量','完整 Python 答案','复杂度与边界样例'])assert.ok(teaching.includes(label),`${entry.id}: ${label}`);
    assert.ok(teaching.includes('def '),`${entry.id}: 可读 Python 答案`);
  }
});
check('SQL九题都有稳定题号、知识解析、答案口述与失败边界',()=>{
  const file='docs/70-practice/sql-nine-worked-problems.md';
  const d=docs.get(file);
  const ids=Array.from({length:9},(_,i)=>`s0${i+1}`);
  assert.equal(d.headings.filter(h=>/^s0[1-9]$/.test(h.id)).length,9);
  for(const id of ids){
    assert.ok(d.headings.some(h=>h.id===id&&h.text.startsWith(id.toUpperCase())),id);
    const section=d.sections.find(s=>s.id===id);
    assert.ok(section,id);
    for(const label of ['知识点详解','面试答法','追问','常见误区'])assert.ok(section.text.includes(label),`${id}: ${label}`);
    const result=engine.query(new URLSearchParams({q:id})).results.find(r=>r.d.path===file);
    assert.ok(result,id);assert.equal(result.section.id,id);
  }
  assert.ok(d.source.includes('MySQL 8.0/8.4'));
  assert.ok(d.source.includes('不能替代 MySQL'));
});
check('收藏与已读筛选仅使用传入的本地状态',()=>{
  const p=data.docs[0].path;
  assert.equal(engine.query(new URLSearchParams({view:'saved'}),{saved:[p],done:[]}).results[0].d.path,p);
  assert.equal(engine.query(new URLSearchParams({view:'saved'}),{saved:[],done:[]}).results.length,0);
  assert.equal(engine.query(new URLSearchParams({view:'done'}),{saved:[],done:[p]}).results.length,1);
});
check('全量教学代码高亮逐字保真，解答和知识区可折叠',()=>{
  const marked=new Marked();
  const unescape=source=>source.replace(/<\/?span\b[^>]*>/g,'').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');
  let blocks=0;
  for(const d of data.docs){
    const expected=[];
    marked.walkTokens(marked.lexer(d.source),token=>{if(token.type==='code')expected.push(token.text);});
    const actual=[...d.html.matchAll(/<pre[^>]*><code>([\s\S]*?)<\/code><\/pre>/g)].map(m=>unescape(m[1]));
    assert.deepEqual(actual,expected,d.path);
    blocks+=actual.length;
  }
  assert.ok(blocks>200,`应检查全量教学代码，而非少数样本：${blocks}`);
  assert.ok(data.docs.find(d=>d.problemId===1).html.includes('class="answer-section"'));
  assert.ok(docs.get('docs/10-agent/01-agent-loop-tools-and-state.md').html.includes('class="knowledge-section"'));
  console.log(`  已逐字核对 ${blocks} 个教学代码块。`);
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
check('知识修订可检索，39条Agent追问参考答案可折叠且题数独立',()=>{
  const expected=[['docs/10-agent/01-agent-loop-tools-and-state.md',8],['docs/10-agent/02-rag-retrieval-and-reranking.md',11],['docs/10-agent/03-memory-and-context.md',5],['docs/10-agent/04-streaming-and-reliable-execution.md',7],['docs/50-projects/public-repository-case-studies.md',8]];
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
  assert.equal(index.counts.interview_questions,364);
  assert.equal(data.hot100Count,100);
  assert.equal(data.supplementaryCount,15);
});
check('26张场景卡编号、搜索、答案、追问与既有题数独立',()=>{
  const scenes=catalog.scenarios;
  assert.equal(data.scenarioCount,26);
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
  assert.equal(data.questionCount,464);assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);
});
check('生产页面脚本非渲染启动：总览、搜索、阅读与禁用存储',()=>{
  // Minimal DOM stubs check runtime initialization only. They do not lay out or paint a page.
  function boot(hash,allowStorage=true,initialState={}){
    const nodes=new Map();
    const stub=()=>({innerHTML:'',textContent:'',value:'',hidden:true,dataset:{},listeners:{},style:{setProperty(){}},classList:{add(){},remove(){},contains(){return false;},toggle(){}},setAttribute(){},removeAttribute(){},getAttribute(){return '';},addEventListener(name,fn){this.listeners[name]=fn;},querySelectorAll(){return [];},contains(){return false;},focus(){this.focused=true;},scrollIntoView(){this.scrolled=true;},select(){}});
    const doc={getElementById(id){if(!nodes.has(id))nodes.set(id,stub());return nodes.get(id);},querySelector(selector){return this.getElementById(selector);},querySelectorAll(){return [];},addEventListener(){},documentElement:stub(),activeElement:null};
    const sandbox={window:{},document:doc,innerWidth:390,location:{hash},URLSearchParams,localStorage:{getItem(){if(!allowStorage)throw Error('disabled');return JSON.stringify(initialState);},setItem(key,value){if(!allowStorage)throw Error('disabled');sandbox.savedState=JSON.parse(value);}},history:{replaceState(a,b,hash){sandbox.location.hash=hash;}},setTimeout(){return 1;},clearTimeout(){},requestAnimationFrame(fn){fn();},getComputedStyle(){return {display:'block'};}};
    sandbox.window.matchMedia=()=>({matches:false});sandbox.window.scrollTo=()=>{};sandbox.window.listeners={};sandbox.window.addEventListener=(name,fn)=>{sandbox.window.listeners[name]=fn;};
    for(const match of html.matchAll(/<script src="(assets\/data\.[^"]+\.js)" defer><\/script>/g))vm.runInNewContext(fs.readFileSync(path.join(site,match[1]),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(dataText,sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/search.js'),'utf8'),sandbox,{timeout:10000});
    vm.runInNewContext(fs.readFileSync(path.join(site,'assets/app.js'),'utf8'),sandbox,{timeout:10000});
    return {html:nodes.get('main').innerHTML,title:doc.title,nodes,sandbox};
  }
  const taxonomy=data.taxonomy;
  const interviewPath='docs/60-interviews/agent-followups-20261015.md';
  const simulation=taxonomy.entries.find(e=>e.id==='simulation:1');
  const originalBack='#/library?'+new URLSearchParams({area:'interviews',company:'bytedance',round:'1',q:'评测',page:'2'});
  const decodeHref=value=>value.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
  const interview=boot('#/read/'+encodeURIComponent(interviewPath)+'?'+new URLSearchParams({section:'p18-answers',area:'interviews',entry:'report:P18',back:originalBack}));
  assert.ok(interview.nodes.get('main').innerHTML.split('<article')[0].includes('字节跳动'));
  const p18Hash=interview.sandbox.location.hash;
  const body=interview.nodes.get('main').innerHTML.split('<article')[1].split('</article>')[0];
  const practice=body.match(/href="([^"]+)"[^>]*>深入练习\s*1<\/a>/);
  assert.ok(practice,'actual rendered body must contain 深入练习1');
  const practiceHref=decodeHref(practice[1]);
  assert.equal(new URLSearchParams(practiceHref.split('?')[1]).get('back'),originalBack);
  interview.sandbox.location.hash=practiceHref;
  interview.sandbox.window.listeners.hashchange();
  const switched=interview.nodes.get('main').innerHTML,header=switched.split('<article')[0];
  assert.ok(header.includes('原创模拟'));assert.ok(!header.includes('字节跳动'));assert.ok(!header.includes('· 一面'));
  assert.equal(decodeHref(switched.match(/class="text-link return-results" href="([^"]+)"/)[1]),originalBack,'same-page context preserves exact filtered return');
  const headings=docs.get(interviewPath).headings;const simAt=headings.findIndex(h=>h.id===simulation.anchor),nested=headings[simAt+1];
  assert.ok(nested.level>headings[simAt].level);
  interview.sandbox.location.hash='#/read/'+encodeURIComponent(interviewPath)+'?'+new URLSearchParams({section:nested.id,area:'interviews',back:originalBack});
  interview.sandbox.window.listeners.hashchange();
  const nestedHeader=interview.nodes.get('main').innerHTML.split('<article')[0];assert.ok(nestedHeader.includes('原创模拟'));assert.ok(!nestedHeader.includes('字节跳动'));
  // Follow a rendered cross-page body link, then emulate history back to P18.
  const renderedBody=interview.nodes.get('main').innerHTML.split('<article')[1].split('</article>')[0];
  const cross=[...renderedBody.matchAll(/href="(#\/read\/[^"]+)"/g)].map(m=>decodeHref(m[1])).find(h=>!h.startsWith('#/read/'+encodeURIComponent(interviewPath)+'?'));
  assert.ok(cross);interview.sandbox.location.hash=cross;interview.sandbox.window.listeners.hashchange();
  assert.equal(new URLSearchParams(cross.split('?')[1]).get('back'),originalBack);
  const crossReturn=decodeHref(interview.nodes.get('main').innerHTML.match(/class="text-link return-results" href="([^"]+)"/)[1]);assert.equal(crossReturn,originalBack);
  interview.sandbox.location.hash=p18Hash;interview.sandbox.window.listeners.hashchange();assert.ok(interview.nodes.get('main').innerHTML.split('<article')[0].includes('字节跳动'));
  const unsafeBack='#/library?'+new URLSearchParams({q:'评测 "<tag>&',page:'2',onclick:'bad'});
  const special=boot('#/read/'+encodeURIComponent(interviewPath)+'?'+new URLSearchParams({section:'p18-answers',back:unsafeBack}));
  const specialBody=special.html.split('<article')[1].split('</article>')[0];
  const specialHref=decodeHref(specialBody.match(/href="([^"]+)"[^>]*>深入练习\s*1<\/a>/)[1]);
  const specialBack=new URLSearchParams(specialHref.split('?')[1]).get('back'),backQuery=new URLSearchParams(specialBack.split('?')[1]);
  assert.equal(backQuery.get('q'),'评测 "<tag>&');assert.equal(backQuery.get('page'),'2');assert.ok(!backQuery.has('onclick'));assert.ok(!specialHref.includes('<tag>'));
  const baiduHref=decodeHref(special.nodes.get('module-nav').innerHTML.match(/href="([^"]+)" data-company-nav="baidu"/)[1]);
  special.sandbox.location.hash=baiduHref;special.sandbox.window.listeners.hashchange();
  assert.ok(special.nodes.get('main').innerHTML.includes('不逐一归属'));assert.ok(special.nodes.get('main').innerHTML.includes('多公司回顾'));
  // Company cards, dropdowns and legacy URLs must agree on report membership.
  const interviewLibrary=boot('#/library?area=interviews');
  const typeSelect=interviewLibrary.html.match(/<select id="filter-subcategory"[\s\S]*?<\/select>/)[0];
  for(const company of taxonomy.companies)assert.ok(!typeSelect.includes(`value="${company.id}"`),company.id+' is a company filter, not a report type');
  assert.ok(typeSelect.includes('value="mixed"'));assert.ok(typeSelect.includes('value="simulation"'));
  for(const company of ['baidu','bytedance']){
    const card=[...interviewLibrary.html.matchAll(/<a href="([^"]+)" data-company-card="([^"]+)">[\s\S]*?<\/a>/g)].find(m=>m[2]===company);
    assert.ok(card,'generated company card '+company);
    const href=decodeHref(card[1]),params=new URLSearchParams(href.split('?')[1]);
    assert.equal(params.get('company'),company);assert.ok(!params.has('subcategory'));
    const expected=taxonomy.entries.filter(e=>e.area==='interviews'&&e.companies?.includes(company)).length;
    assert.ok(card[0].includes(`${expected} 个学习入口`));
    interviewLibrary.sandbox.location.hash=href;interviewLibrary.sandbox.window.listeners.hashchange();
    assert.ok(interviewLibrary.nodes.get('main').innerHTML.includes(`${expected} 个匹配入口`));
    if(company==='baidu'){
      assert.equal(expected,1);
      assert.ok(interviewLibrary.nodes.get('main').innerHTML.includes('不逐一归属'));
      assert.ok(interviewLibrary.nodes.get('main').innerHTML.includes('多公司回顾'));
    }
    const legacyCompany=boot('#/library?'+new URLSearchParams({area:'interviews',subcategory:company}));
    const normalized=new URLSearchParams(legacyCompany.sandbox.location.hash.split('?')[1]);
    assert.equal(normalized.get('company'),company);assert.ok(!normalized.has('subcategory'));
    assert.ok(legacyCompany.html.includes(`${expected} 个匹配入口`));
  }
  const shopeeGuide=boot('#/library?area=interviews&subcategory=shopee');
  assert.ok(shopeeGuide.html.includes('34 个匹配入口'));
  const guideHref=decodeHref(shopeeGuide.html.match(/data-company-guide="shopee" href="([^"]+)"/)[1]);
  assert.ok(guideHref.startsWith('#/read/'+encodeURIComponent('docs/10-agent/34-shopee-agent-interview-playbook.md')+'?'));
  const guideBack=new URLSearchParams(guideHref.split('?')[1]).get('back');
  assert.equal(new URLSearchParams(guideBack.split('?')[1]).get('company'),'shopee');
  shopeeGuide.sandbox.location.hash=guideHref;shopeeGuide.sandbox.window.listeners.hashchange();
  assert.equal(decodeHref(shopeeGuide.nodes.get('main').innerHTML.match(/class="text-link return-results" href="([^"]+)"/)[1]),guideBack);
  const companyToSimulation=boot('#/library?area=interviews&company=bytedance&round=1');
  companyToSimulation.nodes.get('main').listeners.change({target:{dataset:{filter:'subcategory'},value:'simulation'}});
  companyToSimulation.sandbox.window.listeners.hashchange();
  const simulationFilter=new URLSearchParams(companyToSimulation.sandbox.location.hash.split('?')[1]);
  assert.equal(simulationFilter.get('subcategory'),'simulation');assert.ok(!simulationFilter.has('company'));assert.ok(!simulationFilter.has('round'));
  assert.ok(companyToSimulation.nodes.get('main').innerHTML.includes('4 个匹配入口'));
  assert.equal([...companyToSimulation.nodes.get('main').innerHTML.matchAll(/class="result-item"/g)].length,4);
  const knowledgePath='docs/10-agent/01-agent-loop-tools-and-state.md';
  const knowledgeBack='#/library?'+new URLSearchParams({area:'knowledge',subcategory:taxonomy.entries.find(e=>e.path===knowledgePath&&e.area==='knowledge'&&!e.anchor).subcategory,q:'Agent',page:'2'});
  const knowledgeContext=boot('#/read/'+encodeURIComponent(knowledgePath)+'?'+new URLSearchParams({area:'knowledge',back:knowledgeBack}));
  const nextNavigation=markup=>markup.match(/<nav class="reader-next"[\s\S]*?<\/nav>/)[0];
  const chapterPeers=nextNavigation(knowledgeContext.html);
  const followTOC=(reader,section)=>{
    const href=[...reader.nodes.get('main').innerHTML.matchAll(/href="([^"]+)" data-section="([^"]+)"/g)].find(m=>m[2]===section)?.[1];
    assert.ok(href,'actual TOC link: '+section);
    reader.sandbox.location.hash=decodeHref(href);reader.sandbox.window.listeners.hashchange();
  };
  const assertKnowledgeContext=()=>{
    const markup=knowledgeContext.nodes.get('main').innerHTML;
    assert.ok(markup.split('<article')[0].includes('知识点'));
    assert.equal(new URLSearchParams(knowledgeContext.sandbox.location.hash.split('?')[1]).get('area'),'knowledge');
    assert.equal(nextNavigation(markup),chapterPeers,'TOC must preserve chapter learning sequence');
    assert.equal(decodeHref(markup.match(/class="text-link return-results" href="([^"]+)"/)[1]),knowledgeBack);
  };
  followTOC(knowledgeContext,'a01');assertKnowledgeContext();
  // A01's answer is h4 and is deliberately absent from the h2/h3 TOC.
  // Check its deep-link context separately; do not fabricate a clickable TOC item.
  const knowledgeHeadings=docs.get(knowledgePath).headings,a01At=knowledgeHeadings.findIndex(h=>h.id==='a01');
  assert.equal(knowledgeHeadings[a01At+1].level,4);
  const answerRoute=new URLSearchParams(knowledgeContext.sandbox.location.hash.split('?')[1]);answerRoute.set('section',knowledgeHeadings[a01At+1].id);
  knowledgeContext.sandbox.location.hash='#/read/'+encodeURIComponent(knowledgePath)+'?'+answerRoute;knowledgeContext.sandbox.window.listeners.hashchange();assertKnowledgeContext();
  followTOC(knowledgeContext,'a02');assertKnowledgeContext();
  // The same hint must not retain P18's company/round when its TOC enters a simulation.
  followTOC(interview,simulation.anchor);
  const simulationHeader=interview.nodes.get('main').innerHTML.split('<article')[0];
  assert.ok(simulationHeader.includes('原创模拟'));assert.ok(!simulationHeader.includes('字节跳动'));assert.ok(!simulationHeader.includes('· 一面'));
  assert.equal(new URLSearchParams(interview.sandbox.location.hash.split('?')[1]).get('back'),originalBack);

  const tocHref=[...switched.matchAll(/href="([^"]+)" data-section=/g)][0][1];
  assert.equal(new URLSearchParams(tocHref.split('?')[1]).get('back'),originalBack);
  const rag=boot('#/read/'+encodeURIComponent('docs/10-agent/02-rag-retrieval-and-reranking.md')+'?'+new URLSearchParams({area:'knowledge',back:originalBack}));
  const relatedPart=rag.html.split('class="learning-related"')[1].split('</section>')[0];
  const relatedLinks=[...relatedPart.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);
  assert.ok(relatedLinks.some(h=>new URLSearchParams(h.split('?')[1]).get('area')==='interviews'),'related project question changes to its actual area');
  for(const href of relatedLinks)assert.equal(new URLSearchParams(href.split('?')[1]).get('back'),originalBack);
  const filters=boot('#/library?area=interviews&subcategory=mixed&company=baidu&round=1&role=Go&pattern=BFS&structure=数组&project=knowflow&q=机制&page=2');
  filters.nodes.get('main').listeners.change({target:{dataset:{filter:'area'},value:'algorithms'}});
  const changedFilters=new URLSearchParams(filters.sandbox.location.hash.split('?')[1]);
  assert.equal(changedFilters.get('area'),'algorithms');assert.equal(changedFilters.get('q'),'机制');
  for(const field of ['subcategory','project','company','round','role','pattern','structure','page'])assert.ok(!changedFilters.has(field),field);
  assert.ok(boot('#/library?area=qa&subcategory=failure').title.startsWith('故障与验证'));
  // Project groups are views of one article; follow actual list, TOC and related hrefs.
  const projectPath='docs/50-projects/source-code-interview-deep-dive.md';
  const projectList=boot('#/library?area=qa&subcategory=project-depth');
  assert.ok(projectList.html.includes('源码项目与共同练习'));
  assert.ok(projectList.html.includes('24 个匹配入口'));
  assert.ok(projectList.nodes.get('module-nav').innerHTML.includes('data-subnav="qa/project-depth"'));
  for(const project of ['knowflow','researchpilot','shared'])assert.ok(projectList.html.includes('project='+project));
  const projectBack='#/library?'+new URLSearchParams({area:'qa',subcategory:'project-depth',project:'researchpilot'});
  const rp=boot(projectBack);
  assert.ok(rp.html.includes('14 个匹配入口'));
  const projectReadLinks=[...rp.html.matchAll(/class="result-item" href="([^"]+)"/g)].map(m=>decodeHref(m[1]));
  assert.equal(projectReadLinks.length,14);
  const rpHref=projectReadLinks.find(h=>new URLSearchParams(h.split('?')[1]).get('section')==='direction-08');
  assert.ok(rpHref);assert.ok(projectReadLinks.every(h=>h.startsWith('#/read/'+encodeURIComponent(projectPath)+'?')));
  assert.ok(!projectReadLinks.some(h=>new URLSearchParams(h.split('?')[1]).get('section')==='direction-01'));
  rp.sandbox.location.hash=rpHref;rp.sandbox.window.listeners.hashchange();
  const assertProjectReturn=()=>assert.equal(decodeHref(rp.nodes.get('main').innerHTML.match(/class="text-link return-results" href="([^"]+)"/)[1]),projectBack);
  assertProjectReturn();
  followTOC(rp,'direction-01');
  let projectRoute=new URLSearchParams(rp.sandbox.location.hash.split('?')[1]);
  assert.equal(projectRoute.get('area'),'qa');assert.equal(projectRoute.get('subcategory'),'project-depth');
  let projectHeader=rp.nodes.get('main').innerHTML.split('<article')[0];
  assert.ok(projectHeader.includes('项目源码深挖'));
  assert.ok(projectHeader.includes('<p class="entry-context">KnowFlow</p>'));
  assertProjectReturn();
  followTOC(rp,'mock-60');
  projectHeader=rp.nodes.get('main').innerHTML.split('<article')[0];
  assert.ok(projectHeader.includes('共同练习'));assertProjectReturn();
  const projectRelated=rp.nodes.get('main').innerHTML.split('class="learning-related"')[1].split('</section>')[0];
  const projectRelatedLinks=[...projectRelated.matchAll(/href="([^"]+)"/g)].map(m=>decodeHref(m[1]));
  assert.equal(projectRelatedLinks.length,3);
  assert.ok(projectRelatedLinks.some(h=>new URLSearchParams(h.split('?')[1]).get('area')==='algorithms'));
  for(const href of projectRelatedLinks)assert.equal(new URLSearchParams(href.split('?')[1]).get('back'),projectBack);
  rp.sandbox.location.hash=projectRelatedLinks.find(h=>new URLSearchParams(h.split('?')[1]).get('area')==='algorithms');rp.sandbox.window.listeners.hashchange();
  assertProjectReturn();
  const knowledgeRelated=knowledgeContext.nodes.get('main').innerHTML.split('class="learning-related"')[1].split('</section>')[0];
  const depthLink=[...knowledgeRelated.matchAll(/href="([^"]+)"/g)].map(m=>decodeHref(m[1])).find(h=>h.startsWith('#/read/'+encodeURIComponent(projectPath)+'?'));
  assert.ok(depthLink);assert.equal(new URLSearchParams(depthLink.split('?')[1]).get('section'),'direction-01');
  assert.equal(new URLSearchParams(depthLink.split('?')[1]).get('area'),'qa');
  assert.equal(new URLSearchParams(depthLink.split('?')[1]).get('back'),knowledgeBack);
  const projectSaved=boot(projectBack+'&view=saved',true,{saved:[projectPath],done:[projectPath]});
  assert.ok(projectSaved.html.includes('1 个匹配章节'));
  assert.equal([...projectSaved.html.matchAll(/class="result-item"/g)].length,1);
  const projectFilters=boot(projectBack+'&page=2');
  projectFilters.nodes.get('main').listeners.change({target:{dataset:{filter:'subcategory'},value:'concept'}});
  const cleanProjectFilter=new URLSearchParams(projectFilters.sandbox.location.hash.split('?')[1]);
  assert.equal(cleanProjectFilter.get('subcategory'),'concept');assert.ok(!cleanProjectFilter.has('project'));assert.ok(!cleanProjectFilter.has('page'));
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
  assert.ok(migrated.html.includes('继续上次阅读'));
  assert.ok(boot('#/').html.includes('先理解，再讲清'));
  assert.ok(boot('#/').html.includes('场景卡'));
  assert.equal(boot('#/').title,'AI Agent 与后端开发学习手册');
  assert.ok(boot('#/').html.includes('从一个具体问题出发'));
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
  assert.ok(boot('#/library?view=saved',false).html.includes('本地存储不可用'));
  const supplement=boot('#/library?module=supplement').html;
  assert.equal((supplement.match(/class="result-item"/g)||[]).length,15);
  assert.ok(supplement.includes('section=problem-77'));assert.ok(!supplement.includes('外部资源题库'));
  assert.ok(!supplement.includes('外部链接与复习提示'));
  const hotReader=boot('#/read/docs%2F80-hot100%2Fproblems%2F0001-two-sum.md').html;
  const relatedReader=boot('#/read/docs%2F80-hot100%2Fproblems%2F0199-binary-tree-right-side-view.md').html;
  for(const reader of [hotReader,relatedReader])for(const phrase of ['代码随想录','程序员Carl','本题精确讲解','本题 Python 区','相关题迁移','source-view','GitHub 原文','来源与版本见正文'])assert.ok(!reader.includes(phrase),phrase);
  for(const excluded of ['sources/README.md','coverage/VALIDATION.md','errata/README.md','VERSIONS.md','CONTRIBUTING.md','site/README.md','docs/10-agent/SOURCES.md']){
    const hidden=boot('#/read/'+encodeURIComponent(excluded));
    assert.ok(hidden.html.includes('这一页没有找到'),excluded);
    assert.ok(!hidden.html.includes('reader-content'),excluded);
  }
  const filteredState=boot('#/',true,{saved:['sources/README.md','coverage/VALIDATION.md'],done:['VERSIONS.md'],lastPath:'sources/README.md'});
  assert.deepEqual([...filteredState.sandbox.savedState.saved],[]);
  assert.deepEqual([...filteredState.sandbox.savedState.done],[]);
  assert.equal(filteredState.sandbox.savedState.lastPath,'');
  const javaReader=boot('#/read/docs%2F20-java%2F16-executor-failure-followups.md').html;
  assert.ok(javaReader.includes('href="assets/repo/examples/interview_followups/ExecutorFailureLab.java" download="ExecutorFailureLab.java"'));
  assert.ok(!javaReader.includes('source-fallback'),'不应为本地教学代码自动添加GitHub出处入口');
  assert.ok(!javaReader.includes('github.com/minimoster/agent-backend-interview-handbook/blob/'),'本地教学代码只保留本地阅读与下载');
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
  assert.equal(data.questionCount,464);assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);assert.equal(data.scenarioCount,26);
  assert.ok(docs.get('docs/10-agent/24-inference-and-serving-boundaries.md').headings.some(h=>h.id==='kv-memory-budget'));
  assert.ok(!docs.has('chapters/kv_cache_supplement.md'),'KV内容合并到既有章');
});
check('新专题正文检索能定位真实锚点且保留必要协议版本',()=>{
  const expectations=[
    ['校准阈值','docs/10-agent/25-agent-evaluation-and-routing.md'],
    ['MMR','docs/10-agent/30-rag-data-and-chunking-lab.md'],
    ['依赖缓存','docs/40-backend/40-python-fastapi-lab.md'],
    ['ROUND_HALF_UP','docs/70-practice/ai-coding-exercises.md']
  ];
  for(const [q,file] of expectations){const result=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===file);assert.ok(result,`${q}: ${file}`);assert.ok(result.section.id);}
  const modern=docs.get('docs/10-agent/31-tool-mcp-and-skill-contracts.md').source;
  assert.ok(modern.includes('2025-11-25'));
});


check('Transformer原创先修导航、形状搜索与源码保持独立口径',()=>{
  const chapterPath='docs/10-agent/05-transformer-prerequisite.md';
  const chapter=docs.get(chapterPath);
  assert.ok(chapter);
  assert.equal(chapter.source,readingMarkdown(fs.readFileSync(path.join(root,chapterPath),'utf8'),chapterPath));
  assert.equal(data.questionCount-data.hot100Count,364);
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
  assert.ok(docs.has('examples/transformer_prerequisite/README.md'));
  for(const file of ['sources/transformer-prerequisite-references.md','coverage/TRANSFORMER_PREREQUISITE_VALIDATION.md'])assert.ok(!docs.has(file),file);
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
  assert.equal(data.questionCount,464);assert.equal(data.questionCount-data.hot100Count,364);
  assert.equal(data.hot100Count,100);assert.equal(data.supplementaryCount,15);assert.equal(data.scenarioCount,26);
  for(const file of paths){
    const d=docs.get(file);assert.ok(d,file);assert.equal(d.questionIds.length,0);
    assert.equal(index.documents.filter(entry=>entry.relative_path===file).length,1,file);
    assert.ok(!index.items.some(item=>(item.relative_path||item.path)===file),file);
    const anchors=[...d.source.matchAll(/<a id="([^"]+)"><\/a>/g)].map(match=>match[1]);
    assert.ok(anchors.length>=5,file);assert.equal(new Set(anchors).size,anchors.length,file);
    for(const id of anchors)assert.equal(d.headings.filter(h=>h.id===id).length,1,`${file}#${id}`);
  }
  for(const file of ['examples/interview_followups/README.md','examples/go/followup_lifecycle/README.md'])assert.ok(docs.has(file),file);
  for(const file of ['sources/interview-followups/README.md','sources/agent-protocol-references.md','coverage/INTERVIEW_FOLLOWUPS_VALIDATION.md'])assert.ok(!docs.has(file),file);
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
  assert.ok(docs.get('docs/40-backend/41-storage-recovery-followups.md').source.includes('不保证'));
});

check('显式源码下载控件不拆行且脚本样式统一使用构建缓存版本',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8');
  assert.ok(css.includes('.reader-content .resource-download{display:inline-block;white-space:nowrap}'));
  const version=data.sourceHash.slice(0,16);
  for(const file of ['style.css','search.js','app.js'])assert.ok(html.includes(`assets/${file}?v=${version}`),file);
});

check('虾皮Agent补充保留34个唯一题号、教学栏目与独立计数',()=>{
  const file='docs/10-agent/34-shopee-agent-interview-playbook.md';
  const d=docs.get(file);
  const mapping=JSON.parse(fs.readFileSync(path.join(root,'data/shopee-agent-question-map.json'),'utf8'));
  assert.ok(d,file);
  assert.equal(mapping.unique_question_count,34);
  assert.equal(mapping.records.length,34);
  assert.equal(new Set(mapping.records.map(r=>r.id)).size,34);
  assert.deepEqual(mapping.records.map(r=>[r.round,r.original_number]),[1,2].flatMap(round=>Array.from({length:17},(_,i)=>[round,i+1])));
  assert.equal(d.questionIds.length,34);
  assert.equal(data.questionCount,464);
  assert.equal(data.hot100Count,100);
  assert.equal(data.scenarioCount,26);

  assert.equal(data.supplementaryCount,15);
  for(const r of mapping.records){
    assert.equal(r.path,file);
    assert.ok(d.headings.some(h=>h.id===r.anchor&&h.text.includes(r.id)),r.id);
    const section=d.sections.find(s=>s.id===r.anchor);
    assert.ok(section,r.id);
    for(const label of ['新手概念','面试口述','落地设计','指标与失败边界','追问与误区','相关练习'])assert.ok(section.text.includes(label),`${r.id}: ${label}`);
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
  assert.ok(!docs.has('sources/shopee-agent-interview-supplement.md'));
  assert.ok(!docs.has('coverage/SHOPEE_AGENT_VALIDATION.md'));
});

check('检索手算、稳定排序、SQL九题与原创模拟可搜索且主线计数独立',()=>{
  for(const [q,file] of [
    ['unjudged_returned','docs/10-agent/35-retrieval-evaluation-worked-example.md'],
    ['heapreplace','docs/70-practice/retrieval-ranking-algorithms.md'],
    ['独立环','docs/60-interviews/agent-followups-20261015.md']
  ]){
    const result=engine.query(new URLSearchParams({q})).results.find(r=>r.d.path===file);
    assert.ok(result,`${q}: ${file}`);
    assert.ok(docs.get(file).headings.some(h=>h.id===result.section.id),q);
    assert.equal(docs.get(file).questionIds.length,0);
    assert.ok(!/libfile_|file_00000000|oai-library:|INTEGRATION\.md/.test(docs.get(file).source));
  }
  const chapter=docs.get('docs/60-interviews/agent-followups-20261015.md').source;
  assert.equal((chapter.match(/^## [^\n]*原创模拟追问 [1-4]：/gm)||[]).length,4);
  assert.equal(data.questionCount,464);

  assert.equal(data.scenarioCount,26);
  assert.equal((docs.get('docs/70-practice/sql-nine-worked-problems.md').source.match(/^## S0[1-9] /gm)||[]).length,9);
  for(const name of ['retrieval_worked_examples.py','test_retrieval_worked_examples.py','interview_build_forest.py','test_interview_build_forest.py']){
    const relative=`examples/retrieval_worked_examples/${name}`;
    assert.ok(fs.readFileSync(path.join(site,'assets/repo',relative)).equals(fs.readFileSync(path.join(root,relative))),relative);
  }
});

check('阅读内容不暴露私有材料或资料核验元数据',()=>{
  const disallowed=/feishu\.(?:cn|com)|larksuite\.com|私人飞书|私人来源|私有来源|提供给本手册整理|四张有重叠|题目来自[^\n]*图片|provided_interview_material|外部Skill ZIP|未读外部技能ZIP|受限原资料|不完整上传样例|截图省略区域|外部技能包实验|提供材料的专项学习|题目材料用于|材料范围：|未由材料精确给定|猜材料中的/;
  for(const d of data.docs)assert.ok(!disallowed.test(d.source),d.path);
  const mapping=fs.readFileSync(path.join(root,'data/shopee-agent-question-map.json'),'utf8');
  assert.ok(!disallowed.test(mapping));
  assert.ok(!Object.hasOwn(JSON.parse(mapping),'source_type'));
});

check('全文、摘要、搜索段落与下载镜像不残留出处渠道',()=>{
  const provenance=/nowcoder\.(?:com|cn)|programmercarl\.com|bilibili\.com|代码随想录|程序员\s*Carl|作者[：:]|原帖|主题来源|资料来源[：:]|来源渠道|核验日期|来源核查日期/i;
  for(const doc of data.docs){
    assert.ok(!provenance.test(JSON.stringify(doc)),doc.path);
    for(const heading of doc.headings)assert.ok(!/^(?:资料来源|参考资料|参考文献|来源与复验|代码随想录延伸阅读)$/.test(heading.text),`${doc.path}: ${heading.text}`);
  }
  for(const file of walk('site/assets/repo'))assert.ok(!provenance.test(fs.readFileSync(path.join(root,file),'utf8')),file);
  for(const query of ['程序员Carl','代码随想录','nowcoder.com','来源核查日期'])assert.equal(fullEngine.query(new URLSearchParams({q:query})).results.length,0,query);
});

check('公开阅读不出现延伸阅读栏目或书目出处残句',()=>{
  // Match bibliographic language, not technical library/model names. In
  // particular MIT licensing and Microsoft APIs remain valid teaching terms.
  const bibliography=text=>{
    const clean=String(text).replace(/<[^>]*>/g,' ').replace(/\*\*/g,'').replace(/\s+/g,' ');
    return /原论文(?:链接|提供|使用)|作者(?:的|报告|在|实验|研究)|(?:参见|参考|详见|依据|根据|见)[^。！？]{0,80}(?:原论文|论文链接|Stanford\s*《|Microsoft\s+(?:Research|rankerEval)|Cormack|MIT\s*循环不变量)|Stanford\s*(?:《[^》]+》|信息检索(?:教材|导论)|介绍)|Microsoft\s+Research\s*的定义|Cormack\s*等人.{0,40}(?:SIGIR|论文)/i.test(clean);
  };
  for(const text of ['Marked 使用 MIT 许可证。','Microsoft Graph API 需要权限校验。','Microsoft rankerEval 接受排序与相关性输入。','Stanford Alpaca 是模型研究示例。','LoRA、Prefix-Tuning 和 Prompt Tuning 是不同方法。','动态和通讯不能代替原论文、代码、模型卡和官方文档。'])assert.ok(!bibliography(text),text);
  for(const text of ['公式可参见 Stanford《信息检索导论》。','Microsoft Research 的定义区分两个指标。','公式见 Cormack 等人的 SIGIR 2009 原论文。','证明方法可参见MIT循环不变量原理。','见深入练习与其原论文链接。'])assert.ok(bibliography(text),text);
  for(const doc of publishedData.docs){
    const content=[doc.title,doc.summary,doc.html,...doc.headings.map(h=>h.text),...doc.sections.map(s=>s.heading+'\n'+s.text)].join('\n');
    assert.ok(!content.includes('延伸阅读'),doc.path);
    assert.ok(!bibliography(content),doc.path);
  }
});

check('两篇新面经34项均有答案、口述与固定项目边界',()=>{
  const file='docs/60-interviews/agent-followups-20261015.md';
  const chapter=docs.get(file);
  const cards=[...chapter.source.matchAll(/^#### (P(?:18|19)-\d{2}) ([^\n]+)\n([\s\S]*?)(?=^#### |^<a id=|^### |$(?![\s\S]))/gm)];
  const ids=cards.map(m=>m[1]);
  assert.deepEqual(ids,[...Array.from({length:23},(_,i)=>`P18-${String(i+1).padStart(2,'0')}`),...Array.from({length:11},(_,i)=>`P19-${String(i+1).padStart(2,'0')}`)]);
  for(const card of cards){assert.ok(card[3].includes('**答案与口述：**'),card[1]);assert.ok(card[3].includes('**原理与'),card[1]);assert.ok(card[3].length>=180,card[1]);}
  for(const anchor of ['source-question-answers','p18-answers','p19-answers'])assert.ok(chapter.headings.some(h=>h.id===anchor),anchor);
  for(const file of ['docs/10-agent/35-retrieval-evaluation-worked-example.md','docs/70-practice/retrieval-ranking-algorithms.md']){
    const source=docs.get(file).source;
    assert.ok(source.includes('6d5bb13dc74dc03a7a59c74b2396c3b10e84caef'),file);
    assert.ok(source.includes('internal/domain/rag/hybrid.go'),file);
    assert.ok(source.includes('口述版'),file);
  }
  assert.ok(docs.get('docs/10-agent/35-retrieval-evaluation-worked-example.md').source.includes('0.523434'));
  assert.ok(docs.get('docs/70-practice/retrieval-ranking-algorithms.md').source.includes('不能继续无条件声称只用 O(K) 空间'));
  assert.equal(data.questionCount,464);assert.equal(data.scenarioCount,26);
});

check('移动筛选最终级联保持一列或两列和44px控件（非渲染检查）',()=>{
  const css=fs.readFileSync(path.join(site,'assets/style.css'),'utf8').replace(/\/\*[\s\S]*?\*\//g,'');
  // Evaluate source order for the exact class selectors under width media rules.
  // This deliberately checks CSS cascade declarations, not browser layout.
  function declarations(width,selector){
    const result={};
    function visit(text,active=true){
      let offset=0;
      while(offset<text.length){
        const open=text.indexOf('{',offset);if(open<0)break;
        const prelude=text.slice(offset,open).trim();let end=open+1,depth=1;
        while(depth&&end<text.length){if(text[end]==='{')depth++;if(text[end]==='}')depth--;end++;}
        const body=text.slice(open+1,end-1);offset=end;
        if(prelude.startsWith('@media')){
          const max=prelude.match(/max-width:\s*(\d+)px/),min=prelude.match(/min-width:\s*(\d+)px/);
          visit(body,active&&!/\bprint\b/.test(prelude)&&(!max||width<=Number(max[1]))&&(!min||width>=Number(min[1])));
        }else if(active&&prelude.split(',').map(x=>x.trim()).includes(selector)){
          for(const declaration of body.split(';')){const colon=declaration.indexOf(':');if(colon>0)result[declaration.slice(0,colon).trim()]=declaration.slice(colon+1).trim();}
        }
      }
    }
    visit(css);return result;
  }
  for(const width of [320,390,720]){
    const filters=declarations(width,'.filters'),field=declarations(width,'.filter-field'),select=declarations(width,'.filter-field select');
    assert.equal(filters.display,'grid',String(width));
    assert.equal(filters['grid-template-columns'],width<=420?'minmax(0,1fr)':'repeat(2,minmax(0,1fr))',String(width));
    assert.equal(field.width,'100%');assert.equal(field['min-width'],'0');
    assert.equal(select['min-height'],'44px');assert.equal(select['font-size'],'14px');
    assert.equal(declarations(width,'.filter-note')['grid-column'],'1 / -1');
  }
});

check('AI代码审查、成本核算和微服务动机沿用既有入口且练习可下载',()=>{
  const file='docs/10-agent/28-frontier-and-engineering-decisions.md';
  const chapter=docs.get(file);
  for(const anchor of ['ai-coding-responsibility','coding-context'])assert.ok(chapter.headings.some(h=>h.id===anchor),anchor);
  for(const phrase of ['USD 0.0532','USD 0.0932','不是并发预算闸门','失败和重试'])assert.ok(chapter.source.includes(phrase),phrase);
  for(const query of ['未知 预留','同一个AI'])assert.ok(engine.query(new URLSearchParams({q:query})).results.some(r=>r.d.path===file),query);
  const interview='docs/90-interview/01-evidence-based-interview-preparation.md';
  assert.ok(engine.query(new URLSearchParams({q:'模块化单体'})).results.some(r=>r.d.path===interview));
  for(const name of ['cost_ledger.py','test_cost_ledger.py']){
    const resource='examples/agent_costs/'+name;
    assert.ok(chapter.html.includes('assets/repo/'+resource),resource);
    assert.deepEqual(fs.readFileSync(path.join(site,'assets/repo',resource)),fs.readFileSync(path.join(root,resource)));
  }
  assert.equal(data.questionCount,464);assert.equal(data.hot100Count,100);
});

check('现有站点检查入口实际执行分类回归',()=>{execFileSync(process.execPath,['--test',path.join(site,'taxonomy.test.mjs')],{stdio:'inherit'});});

console.log(`\n${checks} 组非渲染检查通过。实际浏览器、屏幕尺寸与辅助技术测试需另行进行。`);
