#!/usr/bin/env node
/** Static, deterministic rendering. Markdown and content-index.json remain the source of truth. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Marked, Renderer } from './vendor/marked.mjs';
import { isReadingDocument, isTeachingResource, isProjectCodeUrl, readingMarkdown } from './reading-policy.mjs';
import { validateTaxonomy } from './taxonomy.mjs';

const site = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(site);
const checkOnly = process.argv.includes('--check');
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain = s => s.replace(/<\/?a\b[^>]*>/g, '').replace(/!?(\[)([^\]]+)\]\([^)]*\)/g, '$2').replace(/\*\*([^*]+)\*\*/g,'$1').replace(/`/g, '').replace(/&(?:amp|lt|gt|quot);/g, x => ({'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"'}[x]));
const slug = s => plain(s).toLowerCase().trim().replace(/[^\p{L}\p{N}_\-\s]/gu,'').replace(/\s+/g,'-');
const walk = dir => fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name,'en')).flatMap(e => e.isDirectory()?walk(`${dir}/${e.name}`):[`${dir}/${e.name}`]);
const contentIndex = JSON.parse(fs.readFileSync(path.join(root,'content-index.json'),'utf8'));
const config = JSON.parse(fs.readFileSync(path.join(site,'config.json'),'utf8'));
const indexed = new Map(contentIndex.documents.map(d=>[d.relative_path||d.path,d]));
const hot = JSON.parse(fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8'));
const hotByPath = new Map(hot.problems.map(p=>[p.doc_path,p]));
const catalogPath = 'data/reading-catalog.json';
const catalogSource = fs.readFileSync(path.join(root,catalogPath),'utf8');
const catalog = JSON.parse(catalogSource);
const supplementaryRecords = catalog.supplementaryProblems;
const scenarios = catalog.scenarios;
if (supplementaryRecords.length !== 15 || new Set(supplementaryRecords.map(p=>p.id)).size !== 15 || supplementaryRecords.some(p=>hot.problems.some(h=>h.id===p.id))) throw Error('算法补充应保留15道独立且不重复计入Hot100的题目。');
if (scenarios.length !== 26 || new Set(scenarios.map(s=>s.card_id)).size !== 26) throw Error('场景练习应有26个唯一SC-A/SC-B编号。');
const scenarioByPath = new Map(scenarios.map(s=>[s.file,s]));
const moduleDefs = [
  ['guide','00-guide','学习路线','01','从哪里开始，怎样复习'],
  ['agent','10-agent','AI Agent','02','工具、检索与可靠执行'],
  ['java','20-java','Java','03','语言、并发与运行机制'],
  ['go','30-go','Go','04','并发、网络与工程实践'],
  ['backend','40-backend','后端基础','05','网络、存储与系统设计'],
  ['projects','50-projects','项目案例','06','把机制串成真实场景'],
  ['interviews','60-interviews','面试练习','07','按问题拆解思路与答案'],
  ['practice','70-practice','实验与练习','08','动手验证，解释失败路径'],
  ['hot100','80-hot100','LeetCode Hot100','09','17 类模式，100 道原创题解'],
  ['supplement','85-algorithm-supplement','算法补充','10','15 道独立练习，理解方法与边界'],
  ['scenarios','90-public-interview-scenarios','场景练习','11','26 张练习卡：问题、答案与追问'],
  ['preparation','90-interview','面试准备','12','用真实证据回答技术与HR追问'],
  ['examples',null,'代码示例','13','运行代码，检验机制与边界']
];
// An explicit teaching registry prevents research notes and validation logs
// from becoming hidden public pages, search hits, or downloadable mirrors.
const files = [...new Set([
  ...['docs','examples'].flatMap(dir=>walk(dir).filter(isReadingDocument)),
  ...['README.md','QUESTION_INDEX.md'].filter(p=>fs.existsSync(path.join(root,p)))
])];
const fileSet = new Set(files);
const readingAliases = config.reading_aliases || {};
const readingSectionAliases = config.reading_section_aliases || {};
for (const [old, alias] of Object.entries(readingAliases)) {
  if (fileSet.has(old) || !old.endsWith('.md') || old.startsWith('../') || !fileSet.has(alias.path)) {
    throw Error(`阅读别名必须从已合并的页面指向现有正文：${old}`);
  }
}
const resourcePaths = new Set();
const brokenLinks = [];
const sourceInputs = ['assets/app.js','assets/search.js','assets/style.css'].map(file=>['site/'+file,fs.readFileSync(path.join(site,file),'utf8')]);
sourceInputs.push(['site/config.json',fs.readFileSync(path.join(site,'config.json'),'utf8')],['content-index.json',fs.readFileSync(path.join(root,'content-index.json'),'utf8')],['docs/80-hot100/manifest.json',fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8')]);
sourceInputs.push([catalogPath,catalogSource]);
const taxonomySource=fs.readFileSync(path.join(root,'data/learning-taxonomy.json'),'utf8');
sourceInputs.push(['data/learning-taxonomy.json',taxonomySource],['site/taxonomy.mjs',fs.readFileSync(path.join(site,'taxonomy.mjs'),'utf8')]);
sourceInputs.push(['site/reading-policy.mjs',fs.readFileSync(path.join(site,'reading-policy.mjs'),'utf8')]);
const docs = [];

for (const file of files) {
  const original = fs.readFileSync(path.join(root,file),'utf8');
  sourceInputs.push([file,original]);
  const source = readingMarkdown(original,file);
  const meta = indexed.get(file)||{};
  const problem = hotByPath.get(file);
  const scenario = scenarioByPath.get(file);
  const moduleId = moduleDefs.find(m=>m[1] && file.startsWith(`docs/${m[1]}/`))?.[0] || 'examples';
  const module = moduleDefs.find(m=>m[0]===moduleId);
  const items = contentIndex.items.filter(i => (i.relative_path||i.path)===file);
  const title = plain(source.match(/^# (.+)$/m)?.[1]||meta.title||file);
  const usedIds = new Set();
  const headings = [];
  const sections = [];
  let anchor = '';
  const renderer = new Renderer();
  const marked = new Marked({gfm:true,breaks:false,renderer});
  const link = (href) => {
    if (/^https?:/i.test(href)) return isProjectCodeUrl(href)?href:'';
    if (/^mailto:/i.test(href)) return '';
    if (/^[a-z][\w+.-]*:/i.test(href)) return '';
    const [local,fragment=''] = href.split('#');
    if (!local) {
      const section=readingSectionAliases[file]?.[decodeURIComponent(fragment)] || decodeURIComponent(fragment);
      return `#/read/${encodeURIComponent(file)}${section?`?section=${encodeURIComponent(section)}`:''}`;
    }
    let decoded;
    try { decoded = decodeURIComponent(local.split('?')[0]); } catch { decoded = local; }
    const target = path.posix.normalize(path.posix.join(path.posix.dirname(file),decoded));
    if (target.startsWith('../') || path.posix.isAbsolute(target)) return '';
    if(target==='site'||target==='site/'||target==='site/index.html')return '#/';
    if (readingAliases[target]) {
      const alias=readingAliases[target];
      const section=alias.sections?.[decodeURIComponent(fragment)] || alias.section || '';
      return `#/read/${encodeURIComponent(alias.path)}${section?`?section=${encodeURIComponent(section)}`:''}`;
    }
    if (fileSet.has(target)) {
      const section=readingSectionAliases[target]?.[decodeURIComponent(fragment)] || decodeURIComponent(fragment);
      return `#/read/${encodeURIComponent(target)}${section?`?section=${encodeURIComponent(section)}`:''}`;
    }
    // Removed metadata links are deliberately not resources or deep links.
    if (target.endsWith('.md')) {
      if(isReadingDocument(target))brokenLinks.push({from:file,href,target});
      return '';
    }
    if (!isTeachingResource(target)) return '';
    const absolute = path.join(root,target);
    if(fs.existsSync(absolute)&&fs.statSync(absolute).isFile()) {
      resourcePaths.add(target);
      return `assets/repo/${target.split('/').map(encodeURIComponent).join('/')}${fragment?`#${encodeURIComponent(fragment)}`:''}`;
    }
    brokenLinks.push({from:file,href,target});
    return `../${href}`;
  };
  renderer.link = function(token) {
    const href = link(token.href||'');
    if(!href)return this.parser.parseInline(token.tokens);
    const external = /^https?:/i.test(href);
    return `<a href="${esc(href)}"${external?' target="_blank" rel="noopener noreferrer"':''}${token.title?` title="${esc(token.title)}"`:''}>${this.parser.parseInline(token.tokens)}</a>`;
  };
  renderer.image = token => `<span class="image-reference">[图示：${esc(token.text)}] <a href="${esc(link(token.href))}">查看原图</a></span>`;
  renderer.html = token => {
    const match = token.text.match(/^\s*<a\s+id=["']([\w-]+)["']\s*>\s*<\/a>\s*$/i);
    if (match) { anchor=match[1]; return ''; }
    return esc(token.text);
  };
  renderer.heading = function(token) {
    let id = anchor || slug(token.text) || 'section';
    anchor = '';
    const base=id; let count=1;
    while(usedIds.has(id)) id=`${base}-${count++}`;
    usedIds.add(id);
    token.readingId=id;
    headings.push({id,text:plain(token.text),level:token.depth});
    return `<h${token.depth} id="${esc(id)}" tabindex="-1">${this.parser.parseInline(token.tokens)}</h${token.depth}>\n`;
  };
  renderer.code = token => {
    const lang=(token.lang||'text').split(/\s/)[0].toLowerCase().replace(/[^\w+-]/g,'')||'text';
    const text=token.text;
    const keywords = new Set('class def return if elif else for while in not and or True False None import from as with try except finally raise yield async await pass break continue lambda public private protected static final void int long boolean new null true false package func type var const struct select case go defer range switch interface map chan make len append fmt err nil BEGIN END SELECT FROM WHERE GROUP BY ORDER HAVING JOIN LEFT RIGHT ON AS AND OR NULL INSERT UPDATE DELETE VALUES SET LIMIT DISTINCT COUNT SUM AVG MAX MIN OVER PARTITION ROW_NUMBER RANK DENSE_RANK commit rollback'.split(' '));
    const tokens=text.match(/(?:#[^\n]*|\/\/[^\n]*|--[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b[a-zA-Z_]\w*\b|\b\d+(?:\.\d+)?\b|[\s\S])/g)||[];
    const highlighted=tokens.map(t=> /^(#|\/\/|--)/.test(t)?`<span class="code-comment">${esc(t)}</span>`:/^["']/.test(t)?`<span class="code-string">${esc(t)}</span>`:keywords.has(t)?`<span class="code-keyword">${esc(t)}</span>`:/^\d/.test(t)?`<span class="code-number">${esc(t)}</span>`:esc(t)).join('');
    return `<div class="code-block"><div class="code-toolbar"><span>${esc(lang)}</span><button type="button" class="copy-code" aria-label="复制 ${esc(lang)} 代码">复制代码</button></div><pre tabindex="0" aria-label="${esc(lang)} 代码，可横向滚动"><code>${highlighted}</code></pre></div>\n`;
  };
  renderer.table = function(token) {
    return `<div class="table-wrap" role="region" aria-label="可横向滚动的数据表" tabindex="0">${Renderer.prototype.table.call(this,token)}</div>`;
  };
  marked.use({renderer});
  const tokens = marked.lexer(source);
  let html='';
  let section={id:'',heading:title,text:''};
  let answerOpen=false;
  let knowledgeOpen=false;
  for (let n=0;n<tokens.length;n++) {
    const token=tokens[n];
    const explicitAnchor=(token.raw||'').trim().match(/^<a\s+id=["']([\w-]+)["']\s*>\s*<\/a>$/i);
    if(explicitAnchor){anchor=explicitAnchor[1];continue;}
    if (token.type==='heading') {
      if(knowledgeOpen){html+='</details>';knowledgeOpen=false;}
      if(answerOpen){html+='</div></details>';answerOpen=false;}
      if(section.text.trim()) sections.push(section);
      const rendered=marked.parser([token]);
      section={id:token.readingId,heading:plain(token.text),text:''};
      if(token.depth>1 && /^(核心思路|为什么正确|Python 实现|参考解法|解答|参考答案|追问[12]：.+)$/.test(plain(token.text))) {
        html+=`<details class="answer-section" id="${esc(token.readingId)}" open><summary>${esc(plain(token.text))}<span class="summary-hint">展开 / 收起</span></summary><div class="answer-content">`;
        answerOpen=true;
      } else html+=rendered;
    } else {
      const isLabel=token.type==='paragraph' && /^\*\*[^*]+\*\*/.test(token.raw||'');
      if(isLabel && knowledgeOpen){html+='</details>';knowledgeOpen=false;}
      if(isLabel && /^\*\*知识点详解\*\*/.test((token.raw||'').trim())) {
        html+='<details class="knowledge-section" open><summary>知识点详解</summary>';
        const body=(token.raw||'').replace(/^\*\*知识点详解\*\*\s*[：:]?\s*/,'');
        if(body.trim())html+=marked.parse(body);
        knowledgeOpen=true;
      } else html+=marked.parser([token]);
      if(token.type!=='html' && token.type!=='space') section.text+=(token.type==='code'?token.text:plain(token.raw||token.text||''))+'\n';
    }
  }
  if(knowledgeOpen) html+='</details>';
  if(answerOpen) html+='</div></details>';
  if(section.text.trim())sections.push(section);
  const summary=sections.map(s=>s.text.split('\n').map(l=>l.trim()).find(l=>l.length>24&&!/^(\[|返回|优先级|官方题目|来源|知识点|官方|EASY|MEDIUM|HARD|ID)/.test(l))).find(Boolean)||module[4];
  const length=plain(source).replace(/\s/g,'').length;
  docs.push({path:file,title,module:moduleId,moduleName:module[2],category:scenario?.category||problem?.category||({'公开面经':'面试练习','原创面经追问与故障诊所':'追问与故障排查'}[meta.category]||meta.category)||module[2],difficulty:problem?.difficulty||null,problemId:problem?.id||null,scenarioCardId:scenario?.card_id||null,questionIds:scenario?[scenario.card_id]:(meta.question_ids||items.map(i=>i.id)),items:items.map(i=>({id:i.id,title:i.title,anchor:i.anchor,priority:i.priority})),priorities:[...new Set(items.map(i=>i.priority).filter(Boolean))],kind:scenario?'scenario':moduleId==='supplement'?'exercise-bank':problem?'problem':path.basename(file)==='README.md'?'overview':'chapter',summary:summary.slice(0,180),minutes:Math.max(1,Math.ceil(length/450)),headings,sections,html});
}
for (const [old, alias] of Object.entries(readingAliases)) {
  const target=docs.find(d=>d.path===alias.path);
  for (const section of new Set([alias.section,...Object.values(alias.sections || {})].filter(Boolean))) {
    if (!target.headings.some(h=>h.id===section)) throw Error(`阅读别名缺少目标段落：${old} -> ${section}`);
  }
}
for (const [file, aliases] of Object.entries(readingSectionAliases)) {
  const target=docs.find(d=>d.path===file);
  for (const section of Object.values(aliases)) {
    if (!target?.headings.some(h=>h.id===section)) throw Error(`旧小节缺少目标段落：${file} -> ${section}`);
  }
}
// Catalogue entries point into one canonical exercise bank. Include nested
// question/analysis/answer sections so each exercise remains fully searchable,
// without creating extra chapter-level saved/read records or Hot100 entries.
const supplementaryResources=supplementaryRecords.map(record=>{
  const bank=docs.find(d=>d.path===record.doc_path);
  const anchor=record.article_anchor;
  const start=bank?.headings.findIndex(h=>h.id===anchor) ?? -1;
  if(!bank||!anchor||start<0)throw Error(`补充题${record.id}缺少稳定阅读锚点：${anchor}`);
  const heading=bank.headings[start];
  let end=start+1;
  while(end<bank.headings.length&&bank.headings[end].level>heading.level)end++;
  const sectionIds=new Set(bank.headings.slice(start,end).map(h=>h.id));
  const text=bank.sections.filter(s=>sectionIds.has(s.id)).map(s=>`${s.id===anchor?'':s.heading+'\n'}${s.text}`).join('\n');
  if(!text.trim())throw Error(`补充题${record.id}缺少教学正文：${anchor}`);
  const section={id:anchor,heading:heading.text,text};
  if(!['EASY','MEDIUM','HARD'].includes(record.difficulty))throw Error(`补充题${record.id}的官方难度未核验，须等待资源整合完成。`);
  return {path:bank.path,title:`${record.id}. ${record.title_zh}`,module:'supplement',moduleName:'算法补充',category:record.topic,difficulty:record.difficulty,problemId:null,resourceProblemId:record.id,questionIds:[`LC${record.id}`],priorities:[],kind:'exercise',targetAnchor:anchor,resourceOrder:record.supplementary_order,summary:record.original_review_prompt,minutes:Math.max(1,Math.ceil(section.text.length/450)),sections:[section]};
});
const taxonomy=validateTaxonomy(JSON.parse(taxonomySource),docs,contentIndex.items);
for(const file of [...resourcePaths].sort()) sourceInputs.push([file,fs.readFileSync(path.join(root,file),'utf8')]);
sourceInputs.push(['site/build.mjs',fs.readFileSync(fileURLToPath(import.meta.url),'utf8')]);
const sourceHash=crypto.createHash('sha256').update(sourceInputs.sort(([a],[b])=>a.localeCompare(b,'en')).map(([file,source])=>`${file}\0${source}`).join('\0')).digest('hex');
const data={schemaVersion:'1.2',taxonomy,readingAliases,readingSectionAliases,sourceHash,questionCount:contentIndex.items.length,hot100Count:hot.problems.length,scenarioCount:scenarios.length,supplementaryCount:supplementaryResources.length,supplementaryResources,modules:moduleDefs.filter(([id])=>(id!=='supplement'||supplementaryResources.length)).map(([id,folder,label,number,description])=>({id,label,number,description,count:id==='scenarios'?scenarios.length:id==='supplement'?supplementaryResources.length:docs.filter(d=>d.module===id).length,countUnit:id==='scenarios'?'张场景卡':id==='supplement'?'道练习':'篇文档'})),hot100Categories:hot.categories.map(c=>c.name),docs};
// Small deterministic external scripts keep the offline reader self-contained.
// The source digest in filenames also prevents stale cache combinations.
const serialized=JSON.stringify(data);
const parts=[];
// Keep each generated script small enough to review as plain UTF-8 text.
const partCharacters=30000;
for(let offset=0;offset<serialized.length;offset+=partCharacters){
  const filename=`data.${sourceHash.slice(0,16)}.${String(parts.length+1).padStart(3,'0')}.js`;
  const literal=JSON.stringify(serialized.slice(offset,offset+partCharacters)).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
  parts.push({filename,content:`window.STUDY_DATA_TEXT = (window.STUDY_DATA_TEXT || "") + ${literal};\n`});
}
const js=`/* Generated by node site/build.mjs. Source SHA-256: ${sourceHash} */\nwindow.STUDY_DATA = JSON.parse(window.STUDY_DATA_TEXT);\ndelete window.STUDY_DATA_TEXT;\n`;
const output=path.join(site,'assets/data.js');
const htmlPath=path.join(site,'index.html');
const originalHtml=fs.readFileSync(htmlPath,'utf8');
const scriptBlock=parts.map(p=>`  <script src="assets/${p.filename}" defer></script>`).join('\n')+'\n  <script src="assets/data.js" defer></script>';
const html=originalHtml.replace(/(?:  <script src="assets\/data\.[^"\n]+\.js" defer><\/script>\n)*  <script src="assets\/data\.js" defer><\/script>/,scriptBlock).replace(/(assets\/(?:app\.js|search\.js|style\.css))(?:\?v=[^"\s]*)?/g,`$1?v=${sourceHash.slice(0,16)}`);
if(checkOnly){
  if(!fs.existsSync(output)||fs.readFileSync(output,'utf8')!==js||originalHtml!==html)throw Error('阅读层数据与源文不一致。请运行 node site/build.mjs 后提交生成文件。');
  for(const p of parts)if(!fs.existsSync(path.join(site,'assets',p.filename))||fs.readFileSync(path.join(site,'assets',p.filename),'utf8')!==p.content)throw Error(`数据分片未更新：${p.filename}`);
  const expected=new Set(parts.map(p=>p.filename));
  for(const file of fs.readdirSync(path.join(site,'assets')).filter(f=>/^data\..+\.js$/.test(f)))if(!expected.has(file))throw Error(`过期数据分片：${file}`);
  for(const file of fs.existsSync(path.join(site,'assets/repo'))?walk('site/assets/repo'):[]){
    const resource=file.slice('site/assets/repo/'.length);
    if(!resourcePaths.has(resource)||!isTeachingResource(resource))throw Error(`非教学资源不应公开镜像：${resource}`);
  }
  for(const file of resourcePaths){
    const derived=path.join(site,'assets/repo',file);
    if(!fs.existsSync(derived)||!fs.readFileSync(derived).equals(fs.readFileSync(path.join(root,file))))throw Error(`源文件资源未更新：${file}`);
  }
}else{
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,js);fs.writeFileSync(htmlPath,html);
  for(const file of fs.readdirSync(path.join(site,'assets')).filter(f=>/^data\..+\.js$/.test(f)))fs.unlinkSync(path.join(site,'assets',file));
  for(const p of parts)fs.writeFileSync(path.join(site,'assets',p.filename),p.content);
  const resources=path.join(site,'assets/repo');
  fs.rmSync(resources,{recursive:true,force:true});
  for(const file of resourcePaths){const out=path.join(resources,file);fs.mkdirSync(path.dirname(out),{recursive:true});fs.copyFileSync(path.join(root,file),out);}
}
console.log(`${checkOnly?'已验证':'已构建'}：${docs.length} 篇文档、${contentIndex.items.length} 个索引条目、${resourcePaths.size} 份关联资源。`);
console.log(`源文摘要：${sourceHash}`);
if(brokenLinks.length){console.error('源文中有无法解析的本地链接：',JSON.stringify(brokenLinks,null,2));process.exitCode=1;}
