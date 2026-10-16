/** Navigation helpers. Canonical Markdown, question IDs and anchors stay unchanged. */
const naturalCollator = new Intl.Collator('zh-CN', {numeric:true, sensitivity:'base'});

export function naturalCompare(a, b) {
  return naturalCollator.compare(String(a ?? ''), String(b ?? ''));
}

export function targetKey(path, anchor='') {
  return `${path}${anchor ? '#'+anchor : ''}`;
}

export function assertTarget(docsByPath, path, anchor='') {
  const doc=docsByPath.get(path);
  if (!doc) throw Error(`教学导航缺少正文：${path}`);
  if (anchor && !doc.headings.some(h=>h.id===anchor)) throw Error(`教学导航缺少锚点：${targetKey(path,anchor)}`);
  return doc;
}

// Search an anchored teaching entry within its own heading subtree; the full
// article remains a single canonical record used by reading and bookmarks.
export function entrySections(doc, anchor='') {
  if (!anchor) return doc.sections;
  const start=doc.headings.findIndex(h=>h.id===anchor);
  if (start<0) throw Error(`教学入口缺少锚点：${targetKey(doc.path,anchor)}`);
  let end=start+1;
  while(end<doc.headings.length && doc.headings[end].level>doc.headings[start].level) end++;
  const ids=new Set(doc.headings.slice(start,end).map(h=>h.id));
  return doc.sections.filter(s=>ids.has(s.id));
}

export function assertUnique(values, label) {
  const seen=new Set();
  for (const value of values) {
    if(seen.has(value)) throw Error(`${label}重复：${value}`);
    seen.add(value);
  }
}

export function validateTaxonomy(registry, docs, items) {
  const byPath=new Map(docs.map(d=>[d.path,d]));
  const areaMap=new Map(registry.areas.map(a=>[a.id,a]));
  if(registry.areas.map(a=>a.id).join(',')!=='knowledge,qa,interviews,algorithms')throw Error('教学导航应有四个固定大类');
  if(registry.guidePath!=='docs/00-guide/expanded-map-and-study-plan.md')throw Error('学习路线必须保持唯一');
  assertUnique(registry.pages.map(p=>p.path),'页面归类');
  assertUnique(registry.entries.map(e=>e.id),'导航入口');
  assertUnique(registry.entries.filter(e=>e.itemId).map(e=>e.itemId),'原题号');
  if(registry.pages.length!==docs.length||registry.pages.some(p=>!byPath.has(p.path)))throw Error('所有阅读页面必须且仅登记一次');
  const actual=registry.entries.filter(e=>e.itemId).map(e=>e.itemId).sort();
  if(JSON.stringify(actual)!==JSON.stringify(items.map(i=>i.id).sort()))throw Error('原题号集合改变');
  for(const record of [...registry.pages,...registry.entries]){
    assertTarget(byPath,record.path,record.anchor||'');
    if(!areaMap.get(record.area)?.subcategories.some(s=>s.id===record.subcategory))throw Error(`未知分类：${record.path}`);
    if(!Number.isFinite(record.displayOrder))throw Error(`入口缺少学习顺序：${record.path}`);
  }
  for(const e of registry.entries){
    if(e.itemId){const original=items.find(i=>i.id===e.itemId);if(targetKey(original.path,original.anchor||'')!==targetKey(e.path,e.anchor||''))throw Error(`原题目标改变：${e.itemId}`);}
    if(e.companies?.some(id=>!registry.companies.some(c=>c.id===id)))throw Error(`公司筛选无定义：${e.id}`);
    if(e.subcategory==='simulation'&&(e.companies?.length||e.rounds?.length))throw Error('原创模拟不得继承公司轮次');
    if(e.roundLabel==='一/二面综合回顾'&&e.rounds.length)throw Error('综合回顾不得按单轮筛选');
  }
  for(const [from,links]of Object.entries(registry.related)){
    assertTarget(byPath,from);
    assertUnique(links.map(l=>targetKey(l.path,l.anchor)),'关联目标');
    for(const link of links){assertTarget(byPath,link.path,link.anchor||'');if(!link.label||!link.relation)throw Error('关联链接缺少教学说明');}
  }
  return registry;
}
