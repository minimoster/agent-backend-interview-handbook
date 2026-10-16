/* Browser-only reader. No analytics, accounts, fetch calls, or remote storage. */
(() => {
  'use strict';
  const data = window.STUDY_DATA;
  const main = document.getElementById('main');
  if (!data) { main.textContent = '阅读数据未加载。请从仓库根目录运行 node site/build.mjs。'; return; }
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = window.STUDY_SEARCH.normalize;
  const byPath = new Map(data.docs.map(d => [d.path, d]));
  const readingAliases = data.readingAliases || {};
  const canonicalPath = path => readingAliases[path]?.path || path;
  const taxonomy=data.taxonomy;
  const catalogueDocs=window.STUDY_SEARCH.catalogue(data);
  const byEntry=new Map(catalogueDocs.map(e=>[e.entryId,e]));
  const areaInfo=id=>taxonomy.areas.find(a=>a.id===id);
  const subInfo=(area,id)=>areaInfo(area)?.subcategories.find(s=>s.id===id);
  const difficultyName = { EASY:'简单', MEDIUM:'中等', HARD:'困难' };
  let state = { saved:[], done:[], lastPath:'', fontSize:17, lineHeight:1.95, theme:'' };
  let storageOK = true;
  try { const old = JSON.parse(localStorage.getItem('zhixing.reader.v1') || '{}'); state = {...state,...old}; } catch { storageOK = false; }
  state.saved = Array.isArray(state.saved) ? [...new Set(state.saved.map(canonicalPath).filter(p => byPath.has(p)))] : [];
  state.done = Array.isArray(state.done) ? [...new Set(state.done.map(canonicalPath).filter(p => byPath.has(p)))] : [];
  state.lastPath = byPath.has(canonicalPath(state.lastPath)) ? canonicalPath(state.lastPath) : '';
  state.fontSize = Math.min(22,Math.max(15,Number(state.fontSize)||17));
  state.lineHeight = [1.8,1.95,2.15].includes(state.lineHeight) ? state.lineHeight : 1.95;
  if (!['light','dark'].includes(state.theme)) state.theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  let route;
  let currentPath = '';
  let observer;
  let searchTimer;
  let toastTimer;
  const search = document.getElementById('global-search');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  const navOpen = document.getElementById('nav-open');
  const theme = document.getElementById('theme-toggle');
  const searchEngine = window.STUDY_SEARCH.create(catalogueDocs);
  // The app's route also lives in the hash. A plain #main navigation would
  // replace the current reading route, so the skip link moves focus directly.
  document.querySelector('.skip-link').addEventListener('click',e=>{
    e.preventDefault();
    main.focus({preventScroll:true});
    main.scrollIntoView({block:'start'});
  });

  function persist() {
    try { localStorage.setItem('zhixing.reader.v1',JSON.stringify(state)); } catch { storageOK = false; }
    document.getElementById('saved-count').textContent = state.saved.length;
    document.getElementById('done-count').textContent = state.done.length;
  }
  function applyPreferences() {
    document.documentElement.dataset.theme = state.theme;
    document.documentElement.style.setProperty('--reader-size',state.fontSize+'px');
    document.documentElement.style.setProperty('--reader-line',state.lineHeight);
    theme.setAttribute('aria-label',`切换到${state.theme==='light'?'深':'浅'}色主题`);
    theme.title = theme.getAttribute('aria-label');
  }
  function toast(message) {
    const element=document.getElementById('toast');
    clearTimeout(toastTimer);element.textContent=message;element.classList.add('visible');
    toastTimer=setTimeout(()=>element.classList.remove('visible'),2800);
  }
  function hashForRead(path, section='', areaHint='') {
    const alias=readingAliases[path];
    if(alias){path=alias.path;section=alias.sections?.[section]||alias.section||'';}
    section=data.readingSectionAliases?.[path]?.[section]||section;
    const target=entryForTarget(path,section,areaHint);
    const back=route?.type==='read'?returnHash(currentEntry()):'';
    if(target)return entryHash({...target,targetAnchor:section},back);
    const q=new URLSearchParams();if(section)q.set('section',section);if(back)q.set('back',back);
    return `#/read/${encodeURIComponent(path)}${q.size?'?'+q.toString():''}`;
  }
  function entryHash(entry,back='') {
    const q=new URLSearchParams({area:entry.area,subcategory:entry.subcategory,entry:entry.entryId||entry.id});
    if(entry.targetAnchor||entry.anchor)q.set('section',entry.targetAnchor||entry.anchor);
    if(back)q.set('back',back);
    return `#/read/${encodeURIComponent(entry.path)}?${q.toString()}`;
  }
  function currentEntry() {
    return entryForTarget(route?.path,route?.query.get('section')||'',route?.query.get('area')||'');
  }
  function entryForTarget(path,section='',area='') {
    const matches=catalogueDocs.filter(e=>e.path===path);
    const scoped=matches.some(e=>e.area===area)?matches.filter(e=>e.area===area):matches;
    const exact=scoped.find(e=>(e.targetAnchor||'')===section);if(exact)return exact;
    const doc=byPath.get(path),position=doc?.headings.findIndex(h=>h.id===section)??-1;
    if(position>=0){
      const ancestors=scoped.filter(e=>{if(!e.targetAnchor)return false;const start=doc.headings.findIndex(h=>h.id===e.targetAnchor);let end=start+1;while(end<doc.headings.length&&doc.headings[end].level>doc.headings[start].level)end++;return start<=position&&position<end;});
      ancestors.sort((a,b)=>doc.headings.findIndex(h=>h.id===b.targetAnchor)-doc.headings.findIndex(h=>h.id===a.targetAnchor));
      if(ancestors.length)return ancestors[0];
    }
    return scoped.find(e=>!e.targetAnchor)||matches.find(e=>!e.targetAnchor);
  }
  function returnHash(entry) {
    const back=route?.query.get('back');
    if(back&&/^#\/library(?:\?|$)/.test(back)){
      const allowed=new Set(['area','subcategory','company','round','role','pattern','structure','difficulty','priority','module','topic','q','view','page']);
      return libraryHash(Object.fromEntries([...new URLSearchParams(back.split('?').slice(1).join('?'))].filter(([key])=>allowed.has(key))));
    }
    return libraryHash({area:entry?.area,subcategory:entry?.subcategory});
  }
  function entryMeta(e) {
    const names=(e.companyNames||[]).join('、');
    return [e.entryKind==='interview'?'面经整理与练习':e.entryKind==='simulation'?'原创模拟':e.entryKind==='project-question'?'原创项目场景':e.entryKind==='scenario'?'原创场景卡':'',names,e.roundLabel,(e.roles||[]).join(' / ')].filter(Boolean).map(esc).join(' · ');
  }

  function sourceDownloads(html) {
    // Downloads are recognized from local teaching-code links alone.
    // They do not depend on any remote fallback or raw Markdown field.
    return html.replace(/<a href="(assets\/repo\/([^"#]+\.(?:py|java|go|mod|sql|json|txt))(?:#[^"]*)?)"([^>]*)>([\s\S]*?)<\/a>/gi,
      (anchor, href, resource, attributes, label) => {
        const filename=esc(decodeURIComponent(resource.split('/').pop()));
        if(/下载/.test(label))return `<a href="${href}"${attributes} download="${filename}">${label}</a>`;
        return `${anchor} <a class="resource-download" href="${href}" download="${filename}" aria-label="下载 ${filename}">下载 ↧</a>`;
      });
  }
  function contextualReadingLinks(html) {
    return html.replace(/(<a\b[^>]*\bhref=")(#\/read\/[^"<>]*)(")/gi,(match,before,href,after)=>{
      try {
        const [encoded,query='']=href.slice('#/read/'.length).replace(/&amp;/g,'&').split('?');
        const path=decodeURIComponent(encoded),section=new URLSearchParams(query).get('section')||'';
        if(!byPath.has(path)&&!readingAliases[path])return match;
        return before+esc(hashForRead(path,section))+after;
      } catch { return match; }
    });
  }
  function libraryHash(params={}) { const q=new URLSearchParams(Object.entries(params).filter(([,v])=>v!==''&&v!=null));return '#/library'+(q.size?'?'+q.toString():''); }
  function navigate(hash, replace=false) {
    if (hash===location.hash) { render(); return; }
    if(replace){history.replaceState(null,'',hash);render();}else location.hash=hash;
  }
  function parseRoute() {
    const raw=location.hash.slice(1)||'/';
    const index=raw.indexOf('?');
    const pathname=index<0?raw:raw.slice(0,index);
    const query=new URLSearchParams(index<0?'':raw.slice(index+1));
    let path='';
    try { path=decodeURIComponent(pathname.replace(/^\/read\//,'')); } catch { path=''; }
    if (pathname.startsWith('/read/') && readingAliases[path]) {
      const alias=readingAliases[path];
      const section=alias.sections?.[query.get('section')] || alias.section || '';
      path=alias.path;
      if(section)query.set('section',section);else query.delete('section');
      history.replaceState(null,'',`#/read/${encodeURIComponent(path)}${query.size?'?'+query.toString():''}`);
    }
    const renamedSection=data.readingSectionAliases?.[path]?.[query.get('section')];
    if(pathname.startsWith('/read/') && renamedSection) {
      query.set('section',renamedSection);
      history.replaceState(null,'',`#/read/${encodeURIComponent(path)}?${query.toString()}`);
    }
    return {type:pathname.startsWith('/read/')?'read':pathname==='/library'?'library':'home',path,query};
  }
  function buildNav() {
    document.getElementById('module-nav').innerHTML=`<a href="#/" class="nav-item" data-nav="home"><span aria-hidden="true">⌂</span><span>学习总览</span></a><a href="${hashForRead(taxonomy.guidePath)}" class="nav-item route-link" data-nav="guide"><span aria-hidden="true">↗</span><span>学习路线</span></a>`+taxonomy.areas.map((a,i)=>`<section class="nav-group"><a href="${libraryHash({area:a.id})}" class="nav-item" data-nav="${a.id}"><span aria-hidden="true">0${i+1}</span><span>${esc(a.label)}</span></a><details class="nav-subcategories"><summary>${esc(a.label)}子类</summary>${a.id==='interviews'?`<span class="nav-group-label">按有资料的公司查找</span>${taxonomy.companies.filter(c=>catalogueDocs.some(e=>e.area==='interviews'&&e.companies?.includes(c.id))).map(c=>`<a href="${esc(libraryHash({area:'interviews',company:c.id}))}" data-company-nav="${esc(c.id)}">${esc(c.label)}</a>`).join('')}<span class="nav-group-label">回顾与原创练习</span>`:''}${a.subcategories.filter(sub=>catalogueDocs.some(e=>e.area===a.id&&e.subcategory===sub.id)&&(a.id!=='interviews'||!taxonomy.companies.some(c=>c.id===sub.id))).map(sub=>`<a href="${libraryHash({area:a.id,subcategory:sub.id})}" data-subnav="${a.id}/${sub.id}">${esc(sub.label)}</a>`).join('')}</details></section>`).join('');
  }

  function highlight(value,terms) {
    const text=String(value||'');
    if(!terms.length)return esc(text);
    const escaped=terms.map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).sort((a,b)=>b.length-a.length);
    const expression=new RegExp('('+escaped.join('|')+')','giu');
    return text.split(expression).map(part=>terms.some(t=>normalize(part)===t)?`<mark>${esc(part)}</mark>`:esc(part)).join('');
  }
  function snippet(text,terms) {
    const clean=String(text||'').replace(/\s+/g,' ').trim();
    const found=terms.map(t=>normalize(clean).indexOf(t)).filter(n=>n>=0);
    const at=found.length?Math.min(...found):0;
    const start=Math.max(0,at-35),end=Math.min(clean.length,start+145);
    return (start?'…':'')+clean.slice(start,end)+(end<clean.length?'…':'');
  }
  function badges(d) {
    return (d.kind==='exercise'||d.kind==='exercise-bank'?'<span class="badge">补充练习</span>':'')+(d.difficulty?`<span class="badge ${d.difficulty.toLowerCase()}">${difficultyName[d.difficulty]}</span>`:'') + d.priorities.map(p=>`<span class="badge priority">${p} 优先级</span>`).join('');
  }
  function art() {
    return `<svg class="hero-art" aria-hidden="true" viewBox="0 0 245 215"><g fill="none" stroke="currentColor" stroke-width="1.15"><circle cx="121" cy="103" r="84" opacity=".1"/><circle cx="121" cy="103" r="63" stroke-dasharray="2 5" opacity=".15"/><path d="M46 76 120 54l75 22v101l-75-22-74 22z" fill="var(--panel)"/><path d="M120 54v101M46 76l74 23 75-23M120 99v74M46 177l74 22 75-22v-101"/><path d="m57 88 49 15m-49-1 49 15m-49-1 35 11m-35 3 44 14m-44 0 24 8m111-64-49 15m49-1-49 15m49-1-35 11m35 3-44 14m44 0-24 8" opacity=".3"/><path d="M23 48h41m139-2h24m-7 0v27M15 143h19m173 21h26" opacity=".3"/><path d="m145 32 11 4 11-4-11-4zM156 36v14" opacity=".7"/></g><g fill="currentColor"><circle cx="44" cy="42" r="3" opacity=".5"/><circle cx="213" cy="128" r="2" opacity=".4"/><circle cx="31" cy="183" r="2" opacity=".4"/></g><text x="157" y="198" fill="currentColor" font-size="7" letter-spacing="1.7" opacity=".5">LEARN · CONNECT</text></svg>`;
  }
  function renderHome() {
    const resume=byPath.get(state.lastPath);main.className='home-main';
    main.innerHTML=`<section class="home-hero"><div><div class="eyebrow">AI Agent 与后端开发学习手册</div><h1 class="home-title">先理解，再讲清。<br><span class="hero-final-clause">把知识用起来。</span></h1><p class="hero-description">从一个具体问题出发：读机制、推例子、试着口述，再用追问和代码查漏补缺。</p><div class="hero-actions"><a class="button primary" href="${hashForRead(taxonomy.guidePath)}">从学习路线开始 →</a>${resume?`<a class="button" href="${hashForRead(resume.path)}">继续上次阅读</a>`:''}</div><div class="hero-stats"><div class="stat"><strong>${data.questionCount}</strong>原有题号不变</div><div class="stat"><strong>17</strong>Hot100 算法主题</div><div class="stat"><strong>4</strong>学习入口</div></div><p class="count-note">364 道讲义题 + 100 道 Hot100；34 项虾皮练习、15 道算法补充与 26 张原创场景卡分别计数。</p></div>${art()}</section><section aria-labelledby="modules-heading"><div class="section-heading"><h2 id="modules-heading">按现在要练的能力进入</h2><p>章节负责理解，题目帮助回忆；多个入口指向同一份正文。</p></div><div class="area-grid">${taxonomy.areas.map((a,i)=>`<section class="area-card"><div class="card-topline"><span class="card-number">0${i+1} / ${esc(a.verb)}</span></div><h3><a href="${libraryHash({area:a.id})}">${esc(a.label)} <span aria-hidden="true">↗</span></a></h3><p>${esc(a.description)}</p><div class="subcategory-links">${a.subcategories.filter(sub=>catalogueDocs.some(e=>e.area===a.id&&e.subcategory===sub.id)).slice(0,6).map(sub=>`<a href="${libraryHash({area:a.id,subcategory:sub.id})}">${esc(sub.label)}</a>`).join('')}</div><a class="text-link" href="${libraryHash({area:a.id})}">查看${esc(a.label)}全部子类 →</a></section>`).join('')}</div></section><div class="home-bottom"><section class="small-section"><h3>用一次自测留下记忆</h3><p>读完后合上答案：解释一个机制，手推一个例子，再说出一个失败条件。卡住的部分留作下次复习。</p></section><section class="small-section"><h3>沿关联链接巩固</h3><p>文末连接前置概念、配套题目与后续练习。题号始终保留；收藏和已读按章节保存，换入口也能接着读。</p><a class="text-link" href="${libraryHash()}">搜索全部资料 →</a></section></div>`;
  }

  function resultRows(params) { return searchEngine.query(params,state); }
  function renderLibrary() {
    const p=route.query,area=p.get('area')||'',sub=p.get('subcategory')||'',q=p.get('q')||'',view=p.get('view')||'';
    const a=areaInfo(area),child=subInfo(area,sub),legacy=data.modules.find(m=>m.id===p.get('module'));
    const title=q?'搜索结果':view==='saved'?'我的收藏':view==='done'?'已读章节':child?.label||a?.label||legacy?.label||'全部学习资料';
    const desc=q?`搜索“${q}”，匹配题号、标题和正文；多个关键词用空格分隔。`:view?'按章节保存的本机记录，不因题目入口增加而重复。':a?.description||legacy?.description||'选择一个学习入口，或搜索明确的题号与关键词。';
    const select=(key,label,options)=>`<div class="filter-field"><label for="filter-${key}">${label}</label><select id="filter-${key}" data-filter="${key}"><option value="">全部${label}</option>${options.map(o=>`<option value="${esc(o.id)}"${o.id===p.get(key)?' selected':''}>${esc(o.label)}</option>`).join('')}</select></div>`;
    const candidates=catalogueDocs.filter(e=>(!area||e.area===area)&&(!sub||e.subcategory===sub));
    const roles=[...new Set(candidates.flatMap(e=>e.roles||[]))].sort();
    const patterns=[...new Set(candidates.flatMap(e=>e.patterns||[]))].sort();
    const structures=[...new Set(candidates.flatMap(e=>e.dataStructures||[]))].sort();
    const {results,terms}=resultRows(p),pageSize=24,totalPages=Math.max(1,Math.ceil(results.length/pageSize)),page=Math.min(totalPages,Math.max(1,Number(p.get('page'))||1));
    const visible=results.slice((page-1)*pageSize,page*pageSize),back=libraryHash(Object.fromEntries(p));
    main.className='library-main';
    main.innerHTML=`<div class="breadcrumb"><a href="#/">学习总览</a>${a?`<span>/</span><a href="${libraryHash({area})}">${esc(a.label)}</a>`:''}<span>/</span><span>${esc(title)}</span></div><div class="page-heading"><div class="eyebrow">${a?esc(a.verb):'查找与复习'}</div><h1>${esc(title)}</h1><p>${esc(desc)}</p></div>${a&&!sub&&!q&&!view?`<nav class="subcategory-grid" aria-label="${esc(a.label)}子类">${a.subcategories.map(c=>{const count=catalogueDocs.filter(e=>e.area===area&&e.subcategory===c.id).length;return count?`<a href="${libraryHash({area,subcategory:c.id})}"><strong>${esc(c.label)}</strong><span>${count} 个学习入口 →</span></a>`:'';}).join('')}</nav>`:''}${area==='interviews'?'<p class="boundary-note">面经为整理与练习。公司标签只用于对应小节；多公司回顾不把每题归属到每家公司。原创项目、模拟与场景卡单列。</p>':''}${legacy?`<p class="boundary-note">当前保留旧专题筛选：${esc(legacy.label)}。</p>`:''}${!storageOK&&view?'<p class="storage-warning">本地存储不可用，记录仅在本次打开期间保留。</p>':''}<section class="filters" aria-label="筛选学习资料">${select('area','学习入口',taxonomy.areas)}${a?select('subcategory','子类',a.subcategories):''}${area==='interviews'?select('company','公司',taxonomy.companies.filter(c=>candidates.some(e=>e.companies?.includes(c.id))))+select('round','明确轮次',[{id:'1',label:'一面'},{id:'2',label:'二面'},{id:'3',label:'三面'}])+select('role','岗位',roles.map(id=>({id,label:id}))):''}${area==='algorithms'?select('structure','数据结构',structures.map(id=>({id,label:id})))+select('pattern','解法模式',patterns.map(id=>({id,label:id})))+select('difficulty','难度',Object.entries(difficultyName).map(([id,label])=>({id,label}))):''}${area==='qa'?select('priority','优先级',['P0','P1','P2'].map(id=>({id,label:id}))):''}<span class="filter-note">${area==='algorithms'?'主题描述问题领域，解法模式描述具体方法；两者分别筛选。':area==='interviews'?'轮次未知不标注；一/二面综合回顾不拆为单轮真题。':'先独立回忆，再打开正文核对。'}</span></section><div class="results-meta" role="status" aria-live="polite"><span>${results.length} 个匹配${view?'章节':'入口'}${results.length>pageSize?` · 第 ${page} / ${totalPages} 页`:''}</span><button class="reset-button" id="reset-filters">清空搜索与筛选</button></div>${results.length?`<div class="result-list">${visible.map(({d,section})=>{const heading=d.targetAnchor?d.title:section&&/^[A-Z]+\d+\b/.test(section.heading)?section.heading:d.title;const target={...d,targetAnchor:d.targetAnchor||section?.id||''};return `<a class="result-item" href="${entryHash(target,back)}"><span class="result-marker" aria-hidden="true">${esc(d.itemId||d.resourceProblemId||d.scenarioCardId||d.id?.startsWith('SP-')&&d.id||'↗')}</span><div><h2 class="result-title">${highlight(heading,terms)}</h2><div class="result-meta"><span>${esc(d.areaName)} · ${esc(d.subcategoryName)}</span>${badges(d)}${entryMeta(d)?`<span>${entryMeta(d)}</span>`:''}${state.saved.includes(d.path)?'<span>☆ 已收藏</span>':''}${state.done.includes(d.path)?'<span>✓ 已读</span>':''}</div>${d.notice?`<p class="entry-notice">${esc(d.notice)}</p>`:''}${d.method?`<p class="entry-method">练习方法：${esc(d.method)}</p>`:''}<p class="result-snippet">${highlight(snippet(section?.text||d.summary,terms),terms)}</p></div><span class="result-arrow" aria-hidden="true">↗</span></a>`;}).join('')}</div>`:'<section class="empty-state"><h2>暂时没有匹配内容</h2><p>试试更短的关键词，或放宽筛选条件。</p><button class="button" id="empty-reset">浏览全部资料</button></section>'}${totalPages>1?`<nav class="pagination" aria-label="搜索结果分页"><button class="button" data-page="${page-1}"${page===1?' disabled':''}>← 上一页</button><span>${page} / ${totalPages}</span><button class="button" data-page="${page+1}"${page===totalPages?' disabled':''}>下一页 →</button></nav>`:''}`;
  }

  function tocLinks(d) {
    const areaHint=currentEntry()?.area||'';
    return d.headings.filter(h=>h.level>1&&h.level<=3).map(h=>`<a href="${hashForRead(d.path,h.id,areaHint)}" data-section="${esc(h.id)}" class="${h.level===3?'toc-sub':''}">${esc(h.text)}</a>`).join('');
  }
  function renderReader() {
    const d=byPath.get(route.path);
    if(!d){main.className='';main.innerHTML='<section class="empty-state"><h1>这一页没有找到</h1><p>路径可能已更新，试试搜索章节标题或题号。</p><a class="button" href="#/library">返回学习资料</a></section>';currentPath='';return;}
    currentPath=d.path;
    state.lastPath=d.path;persist();
    const toc=tocLinks(d);
    const entry=currentEntry(),a=areaInfo(entry.area),child=subInfo(entry.area,entry.subcategory),back=returnHash(entry);
    const peers=catalogueDocs.filter(x=>x.area===entry.area&&x.subcategory===entry.subcategory).sort((x,y)=>x.displayOrder-y.displayOrder||window.STUDY_SEARCH.naturalCompare(x.id,y.id));
    const i=peers.findIndex(x=>x.entryId===entry.entryId),prev=peers[i-1],next=peers[i+1];
    const related=taxonomy.related[d.path]||[];
    const relatedHash=link=>hashForRead(link.path,link.anchor||'');
    const relatedHtml=related.length?`<section class="learning-related" aria-labelledby="related-heading"><h2 id="related-heading">把这一章连起来</h2><ul>${related.map(link=>`<li><span>${esc(link.relation)}</span><div><a href="${relatedHash(link)}">${esc(link.label)}</a>${link.description?`<p>${esc(link.description)}</p>`:''}</div></li>`).join('')}</ul></section>`:'';
    const recall=entry.area==='qa'?'先用 30 秒说出核心机制，再用正文例子补上条件与边界。':entry.area==='algorithms'?'先手推一个边界输入，再解释循环或状态为什么成立。':entry.entryKind==='interview'||entry.entryKind==='simulation'?'先独立回答一轮，再用后续追问检查假设和验证方法。':'';
    main.className='reader-main';
    main.innerHTML=`<div class="breadcrumb"><a href="#/">学习总览</a><span>/</span><a href="${libraryHash({area:entry.area})}">${esc(a.label)}</a><span>/</span><a href="${libraryHash({area:entry.area,subcategory:entry.subcategory})}">${esc(child.label)}</a><span>/</span><span>${esc(entry.title)}</span></div><div class="reader-layout"><div class="reader-column"><header><div class="eyebrow">${d.problemId?'HOT100 / '+esc(d.category):esc(d.moduleName)+' / READ & UNDERSTAND'}</div><h1 class="reader-title">${esc(d.title)}</h1><a class="text-link return-results" href="${esc(back)}">← 返回当前列表</a>${entryMeta(entry)?`<p class="entry-context">${entryMeta(entry)}</p>`:''}${entry.notice?`<p class="boundary-note">${esc(entry.notice)}</p>`:''}${recall?`<p class="recall-prompt">${esc(recall)}</p>`:''}<div class="reader-meta">${badges(d)}<span>约 ${d.minutes} 分钟</span><span>${d.kind==='scenario'?'· 独立原创场景卡':d.kind==='exercise-bank'?'· 算法补充练习':entry.area==='interviews'?'· 教学整理与练习':'· 原创讲义'}</span></div><div class="reader-tools"><button class="button" id="save-doc" aria-pressed="${state.saved.includes(d.path)}">${state.saved.includes(d.path)?'★ 已收藏':'☆ 收藏章节'}</button><button class="button" id="done-doc" aria-pressed="${state.done.includes(d.path)}">${state.done.includes(d.path)?'✓ 已读':'标记已读'}</button><button class="button" id="toggle-answers" aria-pressed="false">收起知识 / 解答</button><div class="text-size-controls"><span>字号</span><button id="font-minus" aria-label="缩小正文字号"${state.fontSize<=15?' disabled':''}>A−</button><button id="font-plus" aria-label="放大正文字号"${state.fontSize>=22?' disabled':''}>A+</button><button id="line-height" aria-label="切换正文行距" title="切换正文行距">↕</button></div></div></header>${toc?`<details class="mobile-toc"><summary>本章目录 · ${d.headings.filter(h=>h.level>1&&h.level<=3).length} 个小节</summary><nav aria-label="本章目录">${toc}</nav></details>`:''}<article class="reader-content" id="reader-content" aria-label="${esc(d.title)}正文">${contextualReadingLinks(sourceDownloads(d.html))}</article>${relatedHtml}<nav class="reader-next" aria-label="同组学习顺序">${prev?`<a href="${entryHash(prev,back)}"><span>← 上一个学习入口</span>${esc(prev.title)}</a>`:''}${next?`<a href="${entryHash(next,back)}"><span>下一个学习入口 →</span>${esc(next.title)}</a>`:''}</nav></div>${toc?`<aside class="toc" aria-label="本章目录"><h2>这一章的主线</h2><nav>${toc}</nav></aside>`:''}</div>`;
    observeHeadings();
  }
  function observeHeadings() {
    observer?.disconnect();
    if(!('IntersectionObserver' in window))return;
    observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(visible[0])markToc(visible[0].target.id);},{rootMargin:'-90px 0px -65% 0px'});
    main.querySelectorAll('.reader-content h2[id],.reader-content h3[id],.reader-content details[id]').forEach(h=>observer.observe(h));
  }
  function markToc(id) { main.querySelectorAll('[data-section]').forEach(a=>a.classList.toggle('active',a.dataset.section===id)); }
  function scrollToSection(id) {
    if(!id){window.scrollTo(0,0);return;}
    const target=document.getElementById(id);
    if(!target||!main.contains(target)){toast('本节锚点未找到，可以在章内目录选择小节。');return;}
    let parent=target.parentElement;
    while(parent&&parent!==main){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}
    if(target.tagName==='DETAILS')target.open=true;
    target.scrollIntoView({block:'start'});markToc(id);
    if(target.matches('h2,h3,h4'))target.focus({preventScroll:true});
    else if(target.tagName==='DETAILS')target.querySelector('summary')?.focus({preventScroll:true});
    const mobile=target.closest('.mobile-toc');if(mobile)mobile.open=false;
  }
  function render() {
    const previous=route;
    route=parseRoute();
    const q=route.type==='library'?route.query.get('q')||'':'';
    if(search.value!==q)search.value=q;
    const active=route.type==='home'?'home':route.type==='read'?(route.path===taxonomy.guidePath?'guide':currentEntry()?.area):route.query.get('area');
    document.querySelectorAll('[data-nav]').forEach(a=>{const on=a.dataset.nav===active;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    const activeEntry=route.type==='read'?currentEntry():null;
    document.querySelectorAll('[data-subnav]').forEach(a=>{const on=a.dataset.subnav===`${activeEntry?.area||route.query.get('area')}/${activeEntry?.subcategory||route.query.get('subcategory')}`;a.classList.toggle('active',on);if(on){a.setAttribute('aria-current','page');const parent=a.closest('details');if(parent)parent.open=true;}else a.removeAttribute('aria-current');});
    document.getElementById('topbar-context').textContent=route.type==='read'?'专注阅读':route.type==='library'?'资料检索':'学习空间';
    // Section or classification changes must refresh breadcrumbs, related links and return context.
    currentPath='';observer?.disconnect();
    if(route.type==='home')renderHome();else if(route.type==='library')renderLibrary();else renderReader();
    const routeTitle=route.type==='read'?(byPath.get(route.path)?.title||'页面未找到'):route.type==='library'?(route.query.get('q')?'搜索结果':subInfo(route.query.get('area'),route.query.get('subcategory'))?.label||areaInfo(route.query.get('area'))?.label||data.modules.find(m=>m.id===route.query.get('module'))?.label||'学习资料'):'';
    document.title=routeTitle?routeTitle+' · AI Agent 与后端开发学习手册':'AI Agent 与后端开发学习手册';
    closeNav();
    if(route.type==='read')requestAnimationFrame(()=>scrollToSection(route.query.get('section')||''));
    else if(!(document.activeElement===search))window.scrollTo(0,0);
  }
  function openNav() { sidebar.inert=false;sidebar.removeAttribute('aria-hidden');sidebar.classList.add('open');backdrop.hidden=false;navOpen.setAttribute('aria-expanded','true');document.querySelector('.workspace').inert=true;document.getElementById('nav-close').focus(); }
  function closeNav() { const wasOpen=sidebar.classList.contains('open');sidebar.classList.remove('open');backdrop.hidden=true;navOpen.setAttribute('aria-expanded','false');sidebar.inert=innerWidth<=960;if(innerWidth<=960)sidebar.setAttribute('aria-hidden','true');else sidebar.removeAttribute('aria-hidden');document.querySelector('.workspace').inert=false;if(wasOpen)navOpen.focus(); }
  async function copyCode(button) {
    const code=button.closest('.code-block').querySelector('code').textContent;
    try {
      if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(code);
      else {const textarea=document.createElement('textarea');textarea.value=code;textarea.className='sr-only';document.body.append(textarea);textarea.select();const copied=document.execCommand('copy');textarea.remove();if(!copied)throw Error('copy unavailable');}
      button.textContent='已复制';toast('代码已复制');setTimeout(()=>{if(button.isConnected)button.textContent='复制代码';},2000);
    }catch{toast('当前浏览器不允许自动复制，请选中代码后手动复制。');}
  }
  search.addEventListener('input',()=>{
    clearTimeout(searchTimer);
    searchTimer=setTimeout(()=>{const old=route.type==='library'?Object.fromEntries(route.query):{};delete old.page;navigate(libraryHash({...old,q:search.value.trim()}),true);},170);
  });
  search.addEventListener('keydown',e=>{if(e.key==='Enter'){clearTimeout(searchTimer);const old=route.type==='library'?Object.fromEntries(route.query):{};delete old.page;navigate(libraryHash({...old,q:search.value.trim()}),true);main.focus();}});
  main.addEventListener('change',e=>{
    const key=e.target.dataset.filter;if(!key)return;
    const p=Object.fromEntries(route.query);p[key]=e.target.value;delete p.page;
    if(key==='module')delete p.topic;
    if(key==='area')for(const child of ['subcategory','company','round','role','pattern','structure','difficulty','priority','module','topic'])delete p[child];
    if(key==='subcategory')for(const child of ['company','round','role','pattern','structure'])delete p[child];
    navigate(libraryHash(p));
  });
  main.addEventListener('click',e=>{
    const button=e.target.closest('button');if(!button)return;
    if(button.classList.contains('copy-code')){copyCode(button);return;}
    if(button.dataset.page){navigate(libraryHash({...Object.fromEntries(route.query),page:button.dataset.page}));return;}
    if(['reset-filters','empty-reset'].includes(button.id)){navigate(libraryHash(route.query.get('view')&&button.id==='reset-filters'?{view:route.query.get('view')}:{}));return;}
    if(button.id==='save-doc'||button.id==='done-doc'){
      const key=button.id==='save-doc'?'saved':'done';const included=state[key].includes(currentPath);
      state[key]=included?state[key].filter(p=>p!==currentPath):[...state[key],currentPath];persist();
      button.setAttribute('aria-pressed',String(!included));button.textContent=key==='saved'?included?'☆ 收藏章节':'★ 已收藏':included?'标记已读':'✓ 已读';
      toast(key==='saved'?(included?'已移除收藏':'已收藏，本机保存'):(included?'已取消已读标记':'已标记已读，本机保存'));
      if(!storageOK)toast('浏览器未允许本地存储，当前记录只在本次打开期间保留。');return;
    }
    if(button.id==='toggle-answers'){
      const collapsed=button.getAttribute('aria-pressed')!=='true';
      main.querySelectorAll('.reader-content details').forEach(d=>d.open=!collapsed);
      button.setAttribute('aria-pressed',String(collapsed));button.textContent=collapsed?'展开知识 / 解答':'收起知识 / 解答';return;
    }
    if(button.id==='font-plus'||button.id==='font-minus'){
      state.fontSize=Math.min(22,Math.max(15,state.fontSize+(button.id==='font-plus'?1:-1)));applyPreferences();persist();
      document.getElementById('font-minus').disabled=state.fontSize<=15;document.getElementById('font-plus').disabled=state.fontSize>=22;
      toast(`正文字号 ${state.fontSize}px`);return;
    }
    if(button.id==='line-height'){const choices=[1.8,1.95,2.15];state.lineHeight=choices[(choices.indexOf(state.lineHeight)+1)%3];applyPreferences();persist();toast(`正文行距 ${state.lineHeight}`);}
  });
  theme.addEventListener('click',()=>{state.theme=state.theme==='light'?'dark':'light';applyPreferences();persist();});
  navOpen.addEventListener('click',openNav);document.getElementById('nav-close').addEventListener('click',closeNav);backdrop.addEventListener('click',closeNav);
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&sidebar.classList.contains('open')){closeNav();return;}
    const editing=/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||'')||document.activeElement?.isContentEditable;
    if((e.key==='/'&&!editing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();search.focus();search.select();}
    if(e.key==='Tab'&&sidebar.classList.contains('open')){
      const focusable=[...sidebar.querySelectorAll('a,button,summary')].filter(el=>getComputedStyle(el).display!=='none');const first=focusable[0],last=focusable.at(-1);
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
    }
  });
  window.addEventListener('hashchange',()=>{clearTimeout(searchTimer);render();});
  window.addEventListener('resize',()=>{if(innerWidth>960)closeNav();});
  buildNav();persist();applyPreferences();render();
})();
