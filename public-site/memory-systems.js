(function () {
  'use strict';
  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) return;
  const comparison = data.roadmap_reference_data.comparison_sets.find(c => c.comparison_id === 'CMP-NVM-DEVICE-SYSTEM');
  const terms = new Map(data.roadmap_reference_data.terms.map(t => [t.term_id, t]));
  const roads = new Map(data.roadmap_artifacts.map(r => [r.roadmap_id, r]));
  const japanese = new Map([...document.querySelectorAll('[data-memory-en]')].map(el => [el, el.textContent]));
  function textElement(tag, text) {const el=document.createElement(tag);el.textContent=text;return el;}
  function render(lang) {
    document.documentElement.lang = lang;
    japanese.forEach((text,el) => {el.textContent=lang==='en'?el.dataset.memoryEn:text;});
    document.title=document.querySelector('.memory-entry-title').textContent+' | OpenFS';
    document.querySelectorAll('[data-language]').forEach(b => {b.setAttribute('aria-pressed',String(b.dataset.language === lang));});
    document.querySelectorAll('[data-memory-link]').forEach(a => {const u=new URL(a.href);u.searchParams.set('lang',lang);a.href=u.href;});
    document.getElementById('memory-comparison-caveat').textContent=comparison['caveat_'+lang];
    const tr=document.createElement('tr');
    for (const label of [lang==='ja'?'技術':'Technology',...comparison.columns.map(c => c['label_'+lang])]) tr.append(textElement('th',label));
    document.getElementById('memory-table-head').replaceChildren(tr);
    const body=document.getElementById('memory-table-body');body.replaceChildren();
    for (const row of comparison.rows) {
      const term=terms.get(row.term_id), line=document.createElement('tr'), label=document.createElement('th'), a=textElement('a',term['label_'+lang]);
      a.href='../glossary/?term='+encodeURIComponent(term.term_id)+'&lang='+lang;label.append(a);line.append(label);
      for (const cell of row.cells) {
        const td=textElement('td',cell['text_'+lang]);
        if(cell.column_id==='evidence') for(const ref of row.source_refs) {
          const source=roads.get(ref.roadmap_id).sources.find(s => s.source_id===ref.source_id);
          const link=textElement('a',(lang==='ja'?'出典':'Source')+(source.published_at?' · '+source.published_at:''));
          link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';link.className='memory-source';td.append(link);
        }
        line.append(td);
      }
      body.append(line);
    }
    for(let index=1;index<=3;index++) window.OpenFSFeedback.mount('memory-feedback-'+index,{kind:'page',id:'MEMORY-SYSTEMS-Q'+index,title:document.getElementById('memory-question-'+index).textContent,relatedIds:['ARCH-03','RM-HW-MEMORY'],path:'memory-systems/'});
  }
  let lang=new URLSearchParams(location.search).get('lang');
  if(!['ja','en'].includes(lang)) {try {lang=localStorage.getItem('openfs-language');} catch (_) {lang='ja';}}
  document.querySelectorAll('[data-language]').forEach(b => b.addEventListener('click',() => {render(b.dataset.language);try {localStorage.setItem('openfs-language',b.dataset.language);} catch (_) {}}));
  render(lang==='en'?'en':'ja');
})();
