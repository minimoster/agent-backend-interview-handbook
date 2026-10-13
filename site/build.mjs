#!/usr/bin/env node
/** Static, deterministic rendering. Markdown and content-index.json remain the source of truth. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Marked, Renderer } from './vendor/marked.mjs';

const site = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(site);
const checkOnly = process.argv.includes('--check');
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain = s => s.replace(/<\/?a\b[^>]*>/g, '').replace(/!?(\[)([^\]]+)\]\([^)]*\)/g, '$2').replace(/\*\*([^*]+)\*\*/g,'$1').replace(/`/g, '').replace(/&(?:amp|lt|gt|quot);/g, x => ({'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"'}[x]));
const slug = s => plain(s).toLowerCase().trim().replace(/[^\p{L}\p{N}_\-\s]/gu,'').replace(/\s+/g,'-');
const walk = dir => fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name,'en')).flatMap(e => e.isDirectory()?walk(`${dir}/${e.name}`):[`${dir}/${e.name}`]);
const contentIndex = JSON.parse(fs.readFileSync(path.join(root,'content-index.json'),'utf8'));
const config = JSON.parse(fs.readFileSync(path.join(site,'config.json'),'utf8'));
if(!/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(config.repository_url)||!config.branch||/[?#]/.test(config.branch))throw Error('site/config.json 需要有效的 GitHub 仓库地址与分支。');
const sourceUrl = (file,fragment='') => `${config.repository_url}/blob/${encodeURIComponent(config.branch)}/${file.split('/').map(encodeURIComponent).join('/')}${fragment?'#'+encodeURIComponent(fragment):''}`;
const indexed = new Map(contentIndex.documents.map(d=>[d.relative_path||d.path,d]));
const hot = JSON.parse(fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8'));
const hotByPath = new Map(hot.problems.map(p=>[p.doc_path,p]));
const carlPath='sources/carl-hot100-resources.json';
const carlSource=fs.existsSync(path.join(root,carlPath))?fs.readFileSync(path.join(root,carlPath),'utf8'):null;
const carl=carlSource?JSON.parse(carlSource):null;
const carlByPath=new Map((carl?.problems||[]).map(p=>[p.doc_path,p]));
const supplementaryRecords=carl?.supplementary_index?.problems||[];
if(carl){
  if(carl.problems.length!==100||supplementaryRecords.length!==15)throw Error('Carl资源应分别保留100个Hot100条目与15个补充条目。');
  const hotIds=new Set(hot.problems.map(p=>p.id));
  if(new Set(carl.problems.map(p=>p.id)).size!==100||carl.problems.some(p=>!hotIds.has(p.id)))throw Error('Carl的100题须与原Hot100题号一致。');
  if(new Set(supplementaryRecords.map(p=>p.id)).size!==15||supplementaryRecords.some(p=>hotIds.has(p.id)))throw Error('补充15题须独立且不重复计入Hot100。');
}
function compactCarl(entry,anchor){
  const checkedUrl=(url,hosts)=>{
    const parsed=new URL(url);
    if(parsed.protocol!=='https:'||!hosts.includes(parsed.hostname))throw Error(`Carl资源包含非预期地址：${url}`);
    return url;
  };
  const videos=(list,direct)=>(list||[]).map(v=>{
    if(v.direct_problem_match!==direct||v.official_author_verified!==true)throw Error(`视频${v.url}的精确/相关标志或作者核验不一致。`);
    return {url:checkedUrl(v.url,['www.bilibili.com','bilibili.com']),label:v.label};
  });
  return {author:'代码随想录（程序员Carl）',checkedDate:entry.checked_date||carl.checked_date,anchor,
    explanation:entry.has_direct_explanation?checkedUrl(entry.primary_explanation_url,['programmercarl.com','www.programmercarl.com']):null,
    python:entry.has_direct_python_implementation?checkedUrl(entry.primary_python_url,['programmercarl.com','www.programmercarl.com']):null,
    directVideos:videos(entry.direct_videos,true),relatedVideos:videos(entry.related_videos,false)};
}
const scenarioMap=JSON.parse(fs.readFileSync(path.join(root,'sources/public-interviews/scenario-map.json'),'utf8'));
const scenarios=scenarioMap.records;
if(scenarios.length!==26||new Set(scenarios.map(s=>s.card_id)).size!==26)throw Error('公开场景应有26个唯一SC-A/SC-B编号。');
const scenarioByPath=new Map(scenarios.map(s=>[s.file,s]));
const moduleDefs = [
  ['guide','00-guide','学习路线','01','从哪里开始，怎样复习'],
  ['agent','10-agent','AI Agent','02','工具、检索与可靠执行'],
  ['java','20-java','Java','03','语言、并发与运行机制'],
  ['go','30-go','Go','04','并发、网络与工程实践'],
  ['backend','40-backend','后端基础','05','网络、存储与系统设计'],
  ['projects','50-projects','项目案例','06','把机制串成真实场景'],
  ['interviews','60-interviews','面经样本','07','带着证据看公开样本'],
  ['practice','70-practice','实验与练习','08','动手验证，解释失败路径'],
  ['hot100','80-hot100','LeetCode Hot100','09','17 类模式，100 道原创题解'],
  ['supplement','85-algorithm-supplement','算法补充资源','10','15 道独立练习，官方外部资源'],
  ['scenarios','90-public-interview-scenarios','公开场景练习','11','26张原创卡：公开主题、追问与验收'],
  ['preparation','90-interview','面试准备','12','用真实证据回答技术与HR追问'],
  ['reference',null,'版本与来源','13','核查日期、证据与权利边界']
];
// Every first-party Markdown target belongs in the same reading registry. A
// Markdown file copied alone into assets/repo would retain relative links whose
// targets were absent. Rendering this complete registry keeps those links local
// and allows chapter/source navigation without changing the canonical files.
const files = [...new Set([
  ...['docs','examples','coverage','errata','sources'].flatMap(dir=>walk(dir).filter(p=>p.endsWith('.md'))),
  ...['README.md','QUESTION_INDEX.md','VERSIONS.md','CONTRIBUTING.md'].filter(p=>fs.existsSync(path.join(root,p))),
  ...(fs.existsSync(path.join(site,'README.md'))?['site/README.md']:[])
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
const sourceInputs = [['site/config.json',fs.readFileSync(path.join(site,'config.json'),'utf8')],['content-index.json',fs.readFileSync(path.join(root,'content-index.json'),'utf8')],['docs/80-hot100/manifest.json',fs.readFileSync(path.join(root,'docs/80-hot100/manifest.json'),'utf8')]];
if(carlSource)sourceInputs.push([carlPath,carlSource]);
const docs = [];

for (const file of files) {
  const source = fs.readFileSync(path.join(root,file),'utf8');
  sourceInputs.push([file,source]);
  const meta = indexed.get(file)||{};
  const problem = hotByPath.get(file);
  const scenario = scenarioByPath.get(file);
  const moduleId = moduleDefs.find(m=>m[1] && file.startsWith(`docs/${m[1]}/`))?.[0] || 'reference';
  const module = moduleDefs.find(m=>m[0]===moduleId);
  const items = contentIndex.items.filter(i => (i.relative_path||i.path)===file);
  const title = meta.title || plain(source.match(/^# (.+)$/m)?.[1]||file);
  const usedIds = new Set();
  const headings = [];
  const sections = [];
  let anchor = '';
  const renderer = new Renderer();
  const marked = new Marked({gfm:true,breaks:false,renderer});
  const link = (href) => {
    if (/^(https?:|mailto:)/i.test(href)) return href;
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
    const external = /^(https?:|mailto:)/i.test(href);
    const asset = href.startsWith('assets/repo/');
    const target = asset?decodeURIComponent(href.slice('assets/repo/'.length).split('#')[0]):'';
    return `<a href="${esc(href)}"${external?' target="_blank" rel="noopener noreferrer"':''}${token.title?` title="${esc(token.title)}"`:''}>${this.parser.parseInline(token.tokens)}</a>${asset?` <a class="source-fallback" href="${esc(sourceUrl(target))}" target="_blank" rel="noopener noreferrer" aria-label="在 GitHub 查看 ${esc(target)}">GitHub ↗</a>`:''}`;
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
  const carlEntry=carlByPath.get(file);
  const carlAnchor=carlEntry?headings.find(h=>h.text==='代码随想录延伸阅读')?.id:null;
  if(carlEntry&&!carlAnchor)throw Error(`${file}缺少Carl延伸阅读段落，须等待内容整合完成后构建。`);
  docs.push({path:file,sourceUrl:sourceUrl(file),title,module:moduleId,moduleName:module[2],category:scenario?.category||problem?.category||meta.category||module[2],difficulty:problem?.difficulty||null,problemId:problem?.id||null,scenarioCardId:scenario?.card_id||null,questionIds:scenario?[scenario.card_id]:(meta.question_ids||items.map(i=>i.id)),items:items.map(i=>({id:i.id,title:i.title,anchor:i.anchor,priority:i.priority})),priorities:[...new Set(items.map(i=>i.priority).filter(Boolean))],kind:scenario?'scenario':moduleId==='supplement'?'resource-bank':problem?'problem':path.basename(file)==='README.md'?'overview':'chapter',summary:summary.slice(0,180),minutes:Math.max(1,Math.ceil(length/450)),headings,sections,html,source,carl:carlEntry?compactCarl(carlEntry,carlAnchor):null});
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
// Catalogue entries point into one canonical Markdown bank. They do not copy
// answers, add algorithms to Hot100, or imply original executable source.
const supplementaryResources=supplementaryRecords.map(record=>{
  const bank=docs.find(d=>d.path===record.doc_path);
  const anchor=record.article_anchor;
  const section=bank?.sections.find(s=>s.id===anchor);
  if(!bank||!anchor||!section)throw Error(`补充题${record.id}缺少稳定阅读锚点：${anchor}`);
  if(!['EASY','MEDIUM','HARD'].includes(record.difficulty))throw Error(`补充题${record.id}的官方难度未核验，须等待资源整合完成。`);
  return {path:bank.path,sourceUrl:sourceUrl(bank.path,anchor),title:`${record.id}. ${record.title_zh}`,module:'supplement',moduleName:'算法补充资源',category:record.topic,difficulty:record.difficulty,problemId:null,resourceProblemId:record.id,questionIds:[`LC${record.id}`,`CARL${record.id}`],priorities:[],kind:'external-resource',targetAnchor:anchor,resourceOrder:record.supplementary_order,summary:record.original_review_prompt,minutes:Math.max(1,Math.ceil(section.text.length/450)),sections:[section],carl:compactCarl(record,anchor)};
});
for(const file of [...resourcePaths].sort()) sourceInputs.push([file,fs.readFileSync(path.join(root,file),'utf8')]);
sourceInputs.push(['site/build.mjs',fs.readFileSync(fileURLToPath(import.meta.url),'utf8')]);
const sourceHash=crypto.createHash('sha256').update(sourceInputs.sort(([a],[b])=>a.localeCompare(b,'en')).map(([file,source])=>`${file}\0${source}`).join('\0')).digest('hex');
const data={schemaVersion:'1.0',readingAliases,readingSectionAliases,repositoryUrl:config.repository_url,sourceHash,checkedDate:hot.checked_date,questionCount:contentIndex.items.length,hot100Count:hot.problems.length,scenarioCount:scenarios.length,publicSelfReportCount:17,supplementaryCount:supplementaryResources.length,supplementaryResources,carlCheckedDate:carl?.checked_date||null,modules:moduleDefs.filter(([id])=>(id!=='supplement'||supplementaryResources.length)).map(([id,folder,label,number,description])=>({id,label,number,description,count:id==='scenarios'?scenarios.length:id==='supplement'?supplementaryResources.length:docs.filter(d=>d.module===id).length,countUnit:id==='scenarios'?'张场景卡':id==='supplement'?'题外部资源':'篇文档'})),hot100Categories:hot.categories.map(c=>c.name),docs};
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
const html=originalHtml.replace(/(?:  <script src="assets\/data\.[^"\n]+\.js" defer><\/script>\n)*  <script src="assets\/data\.js" defer><\/script>/,scriptBlock);
if(checkOnly){
  if(!fs.existsSync(output)||fs.readFileSync(output,'utf8')!==js||originalHtml!==html)throw Error('阅读层数据与源文不一致。请运行 node site/build.mjs 后提交生成文件。');
  for(const p of parts)if(!fs.existsSync(path.join(site,'assets',p.filename))||fs.readFileSync(path.join(site,'assets',p.filename),'utf8')!==p.content)throw Error(`数据分片未更新：${p.filename}`);
  const expected=new Set(parts.map(p=>p.filename));
  for(const file of fs.readdirSync(path.join(site,'assets')).filter(f=>/^data\..+\.js$/.test(f)))if(!expected.has(file))throw Error(`过期数据分片：${file}`);
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
