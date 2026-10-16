/* Shared, dependency-free full-text model: used by the reader and Node tests. */
(() => {
  'use strict';
  const normalize = s => String(s || '').normalize('NFKC').toLocaleLowerCase('zh-CN').replace(/\s+/g,' ').trim();
  const naturalCompare=(a,b)=>String(a??'').localeCompare(String(b??''),'zh-CN',{numeric:true,sensitivity:'base'});
  const projectMatches=(entry,project)=>!project||(entry.projects||[]).includes(project)||(['knowflow','researchpilot'].includes(project)&&(entry.projects||[]).includes('shared'));
  function catalogue(data) {
    const taxonomy=data.taxonomy,byPath=new Map(data.docs.map(d=>[d.path,d]));
    if(!taxonomy)return [...data.docs,...(data.supplementaryResources||[])];
    return taxonomy.entries.map(entry=>{
      const doc=byPath.get(entry.path),area=taxonomy.areas.find(a=>a.id===entry.area),sub=area.subcategories.find(s=>s.id===entry.subcategory);
      let sections=doc.sections;
      if(entry.anchor){const start=doc.headings.findIndex(h=>h.id===entry.anchor);let end=start+1;while(end<doc.headings.length&&doc.headings[end].level>doc.headings[start].level)end++;const ids=new Set(doc.headings.slice(start,end).map(h=>h.id));sections=[{id:entry.anchor,heading:entry.title,text:doc.sections.filter(s=>ids.has(s.id)).map(s=>s.heading+' '+s.text).join('\n')}];}
      const item=doc.items.find(i=>i.id===entry.itemId);
      const supplement=entry.kind==='supplement'?data.supplementaryResources.find(r=>r.path===entry.path&&r.targetAnchor===entry.anchor):null;
      return {...doc,...supplement,...entry,entryId:entry.id,entryKind:entry.kind,kind:entry.kind==='supplement'?'exercise':entry.anchor?'entry':doc.kind,targetAnchor:entry.anchor,areaName:area.label,subcategoryName:sub.label,subcategoryOrder:area.subcategories.indexOf(sub),questionIds:entry.itemId?[entry.itemId]:entry.id.startsWith('SP-')?[entry.id]:supplement?.questionIds||doc.questionIds,priorities:item?.priority?[item.priority]:doc.priorities,sections,summary:entry.anchor?sections[0]?.text||doc.summary:doc.summary,projectNames:(entry.projects||[]).map(id=>taxonomy.projects?.find(p=>p.id===id)?.label||id),companyNames:(entry.companies||[]).map(id=>taxonomy.companies.find(c=>c.id===id)?.label||id)};
    });
  }
  function create(docs) {
    const indexed=docs.map(d=>({doc:d,all:normalize(`${d.title} ${d.problemId||d.resourceProblemId||''} ${d.problemId||d.resourceProblemId?'LC'+(d.problemId||d.resourceProblemId):''} ${d.questionIds.join(' ')} ${d.category} ${d.areaName||''} ${d.subcategoryName||''} ${(d.companyNames||[]).join(' ')} ${(d.projectNames||[]).join(' ')} ${(d.roles||[]).join(' ')} ${d.roundLabel||''} ${(d.patterns||[]).join(' ')} ${(d.dataStructures||[]).join(' ')} ${d.sections.map(s=>s.heading+' '+s.text).join(' ')}`),title:normalize(d.title),sections:d.sections.map(s=>({...s,index:normalize(s.heading+' '+s.text)}))}));
    return {query(params,state={saved:[],done:[]}) {
      const terms=normalize(params.get('q')||'').split(' ').filter(Boolean);
      const module=params.get('module')||'',topic=params.get('topic')||'',difficulty=params.get('difficulty')||'',priority=params.get('priority')||'',view=params.get('view')||'';
      const project=params.get('project')||'';
      const area=params.get('area')||'',subcategory=params.get('subcategory')||'',company=params.get('company')||'',round=params.get('round')||'',pattern=params.get('pattern')||'',role=params.get('role')||'',structure=params.get('structure')||'';
      const results=[];
      for(const item of indexed){
        const d=item.doc;
        if(d.entryId&&d.targetAnchor&&(!view&&!area&&!terms.length&&!company&&!round&&!project&&!pattern&&!role&&!structure&&!(module==='supplement'&&d.entryKind==='supplement')))continue;
        if(!projectMatches(d,project))continue;
        if(area&&d.area!==area||subcategory&&d.subcategory!==subcategory||company&&!(d.companies||[]).includes(company)||round&&!(d.rounds||[]).includes(Number(round))||pattern&&!(d.patterns||[]).includes(pattern)||role&&!(d.roles||[]).includes(role)||structure&&!(d.dataStructures||[]).includes(structure))continue;
        if(d.kind==='exercise-bank'&&module==='supplement'&&!terms.length&&!view)continue;
        if(module&&d.module!==module||topic&&d.category!==topic||difficulty&&d.difficulty!==difficulty||priority&&!d.priorities.includes(priority))continue;
        if(view==='saved'&&!state.saved.includes(d.path)||view==='done'&&!state.done.includes(d.path))continue;
        if(!terms.every(t=>item.all.includes(t)))continue;
        let section=null,score=0;
        if(terms.length){
          score=terms.reduce((sum,t)=>sum+(item.title.includes(t)?100:0),0);
          if(terms.some(t=>d.questionIds.some(id=>normalize(id)===t)))score+=200;
          const id=d.problemId||d.resourceProblemId;
          if(id&&terms.some(t=>t===String(id)||t==='lc'+id))score+=200;
          let bestScore=-1;
          for(const s of item.sections){
            const titleNorm=normalize(s.heading);
            const sectionScore=terms.reduce((sum,t)=>sum+(titleNorm.includes(t)?45:0)+(s.index.includes(t)?5:0),0);
            if(sectionScore>bestScore){bestScore=sectionScore;section=s;}
          }
          score+=Math.max(0,bestScore);
        }
        results.push({d,section,score});
      }
      if(terms.length)results.sort((a,b)=>b.score-a.score||a.d.path.localeCompare(b.d.path,'en'));
      else results.sort((a,b)=>area?(a.d.subcategoryOrder-b.d.subcategoryOrder||a.d.displayOrder-b.d.displayOrder||naturalCompare(a.d.id,b.d.id)):a.d.module==='supplement'&&a.d.module===b.d.module?(a.d.resourceOrder||0)-(b.d.resourceOrder||0):a.d.module==='hot100'&&b.d.module==='hot100'?(a.d.kind==='overview'?-1:b.d.kind==='overview'?1:(a.d.problemId||0)-(b.d.problemId||0)):naturalCompare(a.d.path,b.d.path));
      const seen=new Set();
      const unique=results.filter(({d,section})=>{const key=d.path+'#'+(view?'':d.targetAnchor||section?.id||'');if(seen.has(key))return false;seen.add(key);return true;});
      return {results:unique,terms};
    }};
  }
  const api={normalize,naturalCompare,projectMatches,catalogue,create};
  if(typeof window!=='undefined')window.STUDY_SEARCH=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})();
