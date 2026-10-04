(async function () {
  "use strict";
  const data = await fetch(new URL('data/system-benchmarks.json', document.currentScript.src)).then(r => {if (!r.ok) throw new Error(r.status); return r.json();});
  let language = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'ja';
  let system = new URLSearchParams(location.search).get('system') || 'SYS-RIKYU';
  let family = 'IOR';
  const text = value => typeof value === 'object' && value !== null ? (value[language] || value.en) : value;
  function node(tag, value, parent) { const e = document.createElement(tag); if (value !== undefined) e.textContent = text(value); parent.append(e); return e; }
  function render() {
    document.documentElement.lang = language;
    document.getElementById('benchmark-footer').textContent = language === 'ja' ? 'HPCI-CFSP 公開調査ビュー' : 'HPCI-CFSP public research view';
    document.querySelectorAll('[data-language]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.language === language)));
    document.getElementById('benchmark-title').textContent = language === 'ja' ? 'システム性能評価' : 'System benchmarks';
    document.getElementById('benchmark-intro').textContent = text(data.summary);
    const selector = document.getElementById('benchmark-systems'); selector.replaceChildren();
    data.systems.forEach(s => {const b = node('button', s.name, selector); b.type='button'; b.setAttribute('aria-pressed', String(system === s.id)); b.onclick=() => {system=s.id; render();};});
    const families=document.getElementById('benchmark-families'); families.replaceChildren();
    data.families.forEach(f => {const b=node('button',f,families); b.type='button'; b.setAttribute('aria-pressed', String(family===f)); b.onclick=()=>{family=f; render();};});
    const content=document.getElementById('benchmark-content'); content.replaceChildren();
    const results=data.results.filter(r=>r.system_id===system && r.family===family);
    if (!results.length) node('p', {ja:'検証済みの実測結果は未掲載です。他のシステムの結果から補完していません。',en:'No verified measurement is published for this system and benchmark.'},content);
    results.forEach(r=>{
      const section=node('section',undefined,content); section.className='operational-methodology';
      node('h3',r.title,section); node('p',r.status,section); node('p',r.conditions,section);
      const table=node('table',undefined,section); const head=node('thead',undefined,table); const tr=node('tr',undefined,head);
      [language==='ja'?'指標':'Metric',language==='ja'?'値':'Value',language==='ja'?'単位':'Unit'].forEach(v=>node('th',v,tr));
      const body=node('tbody',undefined,table); r.metrics.forEach(m=>{const row=node('tr',undefined,body);node('th',m.label,row);node('td',m.value === null ? '—' : String(m.value),row);node('td',m.unit,row);});
      node('h4', {ja:'限定事項',en:'Limitations'}, section); const ul=node('ul',undefined,section);r.limitations.forEach(v=>node('li',v,ul));
      node('p',`${r.date} · ${r.software}`,section);
    });
    const notes=node('section',undefined,content);node('h2',{ja:'比較と拡張の条件',en:'Comparison and extension'},notes);node('p',data.comparison_rule,notes);
    data.sources.forEach(s=>{const p=node('p',undefined,notes);const a=node('a',s.title,p);a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';});
  }
  document.querySelectorAll('[data-language]').forEach(b=>b.addEventListener('click',()=>{language=b.dataset.language;const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);render();})); render();
})().catch(error => {document.getElementById('benchmark-content').textContent = 'Benchmark data unavailable'; console.error(error);});
