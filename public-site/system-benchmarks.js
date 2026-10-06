(async function () {
  "use strict";
  const scriptUrl = new URL(document.currentScript.src);
  const dataUrl = new URL('data/system-benchmarks.json', scriptUrl);
  dataUrl.searchParams.set('v', scriptUrl.searchParams.get('v') || '');
  const data = await fetch(dataUrl).then(r => {if (!r.ok) throw new Error(r.status); return r.json();});
  let language = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'ja';
  let system = new URLSearchParams(location.search).get('system') || 'SYS-RIKYU';
  const params = new URLSearchParams(location.search);
  const detailView = !!document.querySelector('[data-benchmark-view="details"]');
  let selectedCase = params.get('case');
  let family = params.get('family') || 'IOR';
  const detailUrl = r => {const u=new URL(detailView ? './' : 'details/',location.href);u.searchParams.set('lang',language);u.searchParams.set('system',system);u.searchParams.set('family',family);if(r)u.searchParams.set('case',r.id);return u;};
  const text = value => typeof value === 'object' && value !== null ? (value[language] || value.en) : value;
  function node(tag, value, parent) { const e = document.createElement(tag); if (value !== undefined) e.textContent = text(value); parent.append(e); return e; }
  function charts(results, parent) {
    const groups = new Map();
    results.forEach(r => r.metrics.filter(m => r.chart_metrics.includes(m.label) && Number.isFinite(m.value)).forEach(m => {
      const key=m.unit+'|'+m.label;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push({r, m});
    }));
    if (!groups.size) return;
    const section=node('section',undefined,parent); section.className='benchmark-charts';
    node('h3',{ja:'ノード数と性能',en:'Performance versus node count'},section);
    node('p',{ja:'線は同じ条件の実測点だけを結びます。欠測区間は結ばず、未測定値を補間しません。点を選ぶと値・反復数と詳細リンクを表示します。',en:'Lines connect measured points under the same conditions. Gaps remain disconnected; no missing values are interpolated. Select a point for its value, trial count and details link.'},section);
    const colors=['#185f9c','#af3f22','#237948','#7c42a4','#8f670d','#087d83','#b32e71'];
    groups.forEach(points=>{
      const unit=points[0].m.unit, metric=points[0].m.label;
      const figure=node('figure',undefined,section); figure.className='benchmark-chart';
      node('figcaption',`${metric} (${unit})`,figure);
      const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
      svg.setAttribute('viewBox','0 0 680 360'); svg.setAttribute('role','group'); svg.setAttribute('aria-label',`${language==='ja'?'ノード数と性能':'Performance versus nodes'} (${unit})`); figure.append(svg);
      const draw=(tag,attrs,value)=>{const e=document.createElementNS(svg.namespaceURI,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(value!==undefined)e.textContent=value;svg.append(e);return e;};
      const maxY=Math.max(...points.map(p=>p.m.value),1)*1.15;
      const counts=[...new Set(points.map(p=>p.r.nodes))].sort((a,b)=>a-b);
      const logarithmic=counts[counts.length-1]/counts[0]>=16;
      const transform=n=>logarithmic?Math.log2(n):n;
      const minX=logarithmic?transform(counts[0])-0.25:Math.max(0,counts[0]-0.5), maxX=transform(counts[counts.length-1])+(logarithmic?0.25:0.5);
      const x=n=>90+(transform(n)-minX)/(maxX-minX)*550, y=v=>300-v/maxY*245;
      for(let i=0;i<=4;i++) {const value=maxY*i/4; draw('line',{x1:90,x2:640,y1:y(value),y2:y(value),stroke:'#d5dce6'});draw('text',{x:80,y:y(value)+4,'text-anchor':'end'},value.toLocaleString(language,{maximumSignificantDigits:4}));}
      draw('line',{x1:90,x2:640,y1:300,y2:300,stroke:'#566476'});
      counts.forEach(n=>{draw('line',{x1:x(n),x2:x(n),y1:300,y2:306,stroke:'#566476'});draw('text',{x:x(n),y:323,'text-anchor':'middle'},n);});
      draw('text',{x:365,y:349,'text-anchor':'middle'},language==='ja'?(logarithmic?'ノード数（対数軸）':'ノード数'):(logarithmic?'Nodes (logarithmic axis)':'Nodes'));
      draw('text',{x:20,y:177,transform:'rotate(-90 20 177)','text-anchor':'middle'},`${language==='ja'?'性能':'Performance'} (${unit})`);
      const selected=node('p',{ja:'測定点をクリック、またはTabで選択してください。',en:'Click a point or select it with Tab.'},figure); selected.className='benchmark-point-details';selected.setAttribute('aria-live','polite');
      const legend=node('ol',undefined,figure);legend.className='benchmark-legend';
      const series=new Map();
      points.forEach(p=>{const key=p.r.title.en+'|'+p.m.label;if(!series.has(key))series.set(key,[]);series.get(key).push(p);});
      const expected=[...new Set(results.map(r=>r.nodes))].sort((a,b)=>a-b);
      series.forEach((members,key)=>{
        const color=colors[[...series.keys()].indexOf(key)%colors.length];
        const ordered=[...members].sort((a,b)=>a.r.nodes-b.r.nodes);
        let segment=[];
        const flush=()=>{if(segment.length>1)draw('polyline',{points:segment.map(p=>`${x(p.r.nodes)},${y(p.m.value)}`).join(' '),fill:'none',stroke:color,'stroke-width':3,'data-series':key,'data-nodes':segment.map(p=>p.r.nodes).join(',')});segment=[];};
        ordered.forEach(p=>{if(segment.length && expected.indexOf(p.r.nodes)!==expected.indexOf(segment[segment.length-1].r.nodes)+1)flush();segment.push(p);});flush();
        const item=node('li',undefined,legend);item.style.borderLeft=`4px solid ${color}`;node('span',members[0].r.title,item);
        members.forEach(({r,m})=>{
          const count=r.metrics.find(v=>v.label==='Successful trials');
          const label=`${text(r.title)}: ${m.value} ${unit} · ${r.nodes} ${language==='ja'?'ノード':'node(s)'}${count ? ` · N=${count.value}` : ''}`;
          const circle=draw('circle',{cx:x(r.nodes),cy:y(m.value),r:6,fill:color,stroke:'#fff','stroke-width':2,tabindex:0,role:'button','aria-label':label,'data-nodes':r.nodes,'data-series':key});
          const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=label;circle.append(title);
          const select=()=>{selected.replaceChildren();node('span',label,selected);const a=node('a',{ja:'測定条件・コマンド・全数値',en:'Conditions, commands and all values'},selected);a.href=detailUrl(r).href;};
          circle.addEventListener('click',select);circle.addEventListener('focus',select);circle.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select();}});
        });
      });
    });
  }
  function render() {
    document.documentElement.lang = language;
    const viewUrl=new URL(location.href);viewUrl.searchParams.set('lang',language);viewUrl.searchParams.set('system',system);viewUrl.searchParams.set('family',family);if(selectedCase)viewUrl.searchParams.set('case',selectedCase);else viewUrl.searchParams.delete('case');history.replaceState(null,'',viewUrl);
    document.getElementById('benchmark-footer').textContent = language === 'ja' ? 'HPCI-CFSP 公開調査ビュー' : 'HPCI-CFSP public research view';
    document.querySelectorAll('[data-language]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.language === language)));
    document.getElementById('benchmark-title').textContent = detailView ? (language === 'ja' ? '測定条件・詳細' : 'Measurement details') : (language === 'ja' ? 'システム性能評価' : 'System benchmarks');
    document.getElementById('benchmark-intro').textContent = detailView ? text(data.summary) : text({ja:'ノード数に対する実測性能を比較します。条件の異なる系列は別に解釈してください。',en:'Compare measured performance versus node count. Interpret series with different conditions separately.'});
    const selector = document.getElementById('benchmark-systems'); selector.replaceChildren();
    data.systems.forEach(s => {const b = node('button', s.name, selector); b.type='button'; b.setAttribute('aria-pressed', String(system === s.id)); b.onclick=() => {system=s.id; selectedCase=null; render();};});
    const families=document.getElementById('benchmark-families'); families.replaceChildren();
    data.families.forEach(f => {const b=node('button',f,families); b.type='button'; b.setAttribute('aria-pressed', String(family===f)); b.onclick=()=>{family=f; selectedCase=null; render();};});
    const content=document.getElementById('benchmark-content'); content.replaceChildren();
    const results=data.results.filter(r=>r.system_id===system && r.family===family && (!detailView || !selectedCase || r.id===selectedCase));
    if(detailView){const back=node('a',{ja:'性能グラフへ戻る',en:'Back to performance graphs'},content);const u=new URL('../',location.href);u.searchParams.set('lang',language);u.searchParams.set('system',system);u.searchParams.set('family',family);back.href=u.href;}
    if (!results.length) {node('p', {ja:'検証済みの実測結果は未掲載です。他のシステムの結果から補完していません。',en:'No verified measurement is published for this system and benchmark.'},content);return;}
    if(!detailView){
      if(family==='IOR' || family==='mdtest') node('p',{ja:'通常は9反復、64ノードIOR hardは成功3反復。最大値は反復数に依存します。256ノードIOR hardは欠測。buffered I/O・cache flushなし、公式IO500スコアではありません。従来64 GiBと固定総量512 GiB easyは別系列です。',en:'Usually 9 trials; 64-node IOR hard has 3 successful trials. Maximum depends on trial count. 256-node IOR hard is missing. Buffered I/O, no cache flush; not an official IO500 score. Legacy 64 GiB and fixed-total 512 GiB easy are separate series.'},content);
      if(family==='MLPerf Storage') node('p',{ja:'掲載結果は実験pilotです。1回の実行内のepochsは独立反復ではなく、公式スコアではありません。',en:'These are experimental pilots. Epochs within one run are not independent trials; no official score is claimed.'},content);
      charts(results,content);const link=node('a',{ja:'測定条件・コマンド・数値一覧・詳細説明',en:'Measurement conditions, commands, values and explanations'},content);link.className='benchmark-detail-link';link.href=detailUrl().href;return;
    }
    results.forEach(r=>{
      const section=node('section',undefined,content); section.className='operational-methodology';
      node('h3',r.title,section); node('p',r.status,section); node('p',r.conditions,section);
      const table=node('table',undefined,section); const head=node('thead',undefined,table); const tr=node('tr',undefined,head);
      [language==='ja'?'指標':'Metric',language==='ja'?'値':'Value',language==='ja'?'単位':'Unit'].forEach(v=>node('th',v,tr));
      const body=node('tbody',undefined,table); r.metrics.forEach(m=>{const row=node('tr',undefined,body);node('th',m.label,row);node('td',m.value === null ? '—' : String(m.value),row);node('td',m.unit,row);});
      node('h4', {ja:'限定事項',en:'Limitations'}, section); const ul=node('ul',undefined,section);r.limitations.forEach(v=>node('li',v,ul));
      node('p',`${r.date} · ${r.software}`,section);
      const details=node('details',undefined,section);details.className='benchmark-reproduction';
      node('summary',{ja:'使用コマンド・再現条件を表示',en:'Show executed commands and reproduction conditions'},details);
      r.reproduction.notes.forEach(note=>node('p',note,details));
      const pre=node('pre',undefined,details);node('code',r.reproduction.commands,pre);
    });
    const notes=node('section',undefined,content);node('h2',{ja:'比較と拡張の条件',en:'Comparison and extension'},notes);node('p',data.comparison_rule,notes);
    data.sources.forEach(s=>{const p=node('p',undefined,notes);const a=node('a',s.title,p);a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';});
  }
  document.querySelectorAll('[data-language]').forEach(b=>b.addEventListener('click',()=>{language=b.dataset.language;const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);render();})); render();
})().catch(error => {document.getElementById('benchmark-content').textContent = 'Benchmark data unavailable'; console.error(error);});
