(function () {
  "use strict";
  const model = window.OpenFSOperationalModel;
  const colors = ["#087e8b", "#ae4671", "#b66b00", "#365fbc", "#52772c", "#8645a3"];
  const words = {
    ja: {all:"すべて", category:"分類", group:"機能・比較対象", trend:"傾向", confidence:"推定確度", count:"月別ユニークジョブ観測数の合計", share:"対応ジョブ比率 (%)", graph:"グラフ", table:"表", monthly:"月次比較", compare:"比較", name:"名称", empty:"この条件に合う公開観測値はありません。未利用を意味しません。", missing:"抑制／未観測", close:"閉じる", month:"月", jobs:"月別ユニークジョブ数", limit:"比較は最大6系列です。", note:"分類は用途の整理であり、互換性を保証しません。同一ジョブが複数の行に含まれるため、比率は合計できません。", appNote:"パッケージ名は実行アプリケーションを確定する情報ではありません。基盤ソフトウェアと科学アプリケーションの手掛かりを区別しています。", monthlyNote:"欠測・抑制値はゼロにせず、線をつなぎません。系列間の差から非公開値を逆算しません。", expanding:"増加", declining:"減少", stable:"横ばい", "newly-observed":"新規観測", "insufficient-evidence":"証拠不足", low:"低", medium:"中", high:"高", unknown:"未確認"},
    en: {all:"All", category:"Category", group:"Function / comparison group", trend:"Trend", confidence:"Inference confidence", count:"Sum of monthly unique-job observations", share:"Mapped-job share (%)", graph:"Chart", table:"Table", monthly:"Compare monthly trends", compare:"Compare", name:"Name", empty:"No published observations match these filters. This does not establish non-use.", missing:"suppressed / unobserved", close:"Close", month:"Month", jobs:"Monthly unique jobs", limit:"Compare up to six series.", note:"Categories describe function, not interchangeability. Jobs may appear in multiple rows, so shares must not be added.", appNote:"Package names do not establish which application ran. Supporting software is distinguished from scientific-application signals.", monthlyNote:"Missing or suppressed values are not zero; lines break across gaps. Differences are not used to reconstruct withheld values.", expanding:"expanding", declining:"declining", stable:"stable", "newly-observed":"newly observed", "insufficient-evidence":"insufficient evidence", low:"low", medium:"medium", high:"high", unknown:"unverified"}
  };
  function mount(container, data, kind, language) {
    const t = (key) => words[language][key] || key;
    const format = (n) => Number.isFinite(n) ? n.toLocaleString(language === "ja" ? "ja-JP" : "en-US") : t("missing");
    const node = (tag, content, cls) => { const n = document.createElement(tag); if(content !== undefined) n.textContent = content; if(cls) n.className = cls; return n; };
    const button = (label, action, cls) => {const b = node("button",label,cls); b.type="button"; b.addEventListener("click",action); return b;};
    const rows = kind === "software" ? data.families : data.signals;
    const controls = node("div",undefined,"operational-controls");
    const output = node("div");
    const notice = node("p","","operational-note");
    notice.setAttribute("role","status");
    const categoryLabel = (key) => model.categories[key]?.[language === "ja" ? 0 : 1] || key;
    let mode = "table";
    const selected = new Set();
    const select = (key, options) => {
      const label = node("label", t(key));
      const control = node("select");
      control.dataset.filter = key;
      options.forEach(([value,title]) => {const option=node("option",title); option.value=value; control.append(option);});
      label.append(control); controls.append(label); return control;
    };
    const categories = kind === "software" ? ["programming","numerical","communication","ai","runtime","unclassified"] : ["molecular","electronic","chemistry","support","unclassified"];
    const category = select("category", [["all",t("all")],...categories.map((key)=>[key,categoryLabel(key)])]);
    const group = select("group", [["all",t("all")],...[...new Set(rows.map((row)=>model.classify(row,kind).group))].sort().map((key)=>[key,key==="unclassified"?categoryLabel(key):key])]);
    const trend = select("trend", [["all",t("all")],...["expanding","declining","newly-observed","stable","insufficient-evidence"].map((key)=>[key,t(key)])]);
    const confidence = kind === "application" ? select("confidence", [["all",t("all")],...["high","medium","low"].map((key)=>[key,t(key)])]) : null;
    const metric = select("count", [["count",t("count")],["share",t("share")]]);
    metric.parentElement.firstChild.textContent = language === "ja" ? "指標" : "Metric";
    const modes = node("div",undefined,"operational-segmented");
    modes.setAttribute("role","group"); modes.setAttribute("aria-label",language==="ja"?"表示形式":"View");
    const buttons = ["table","graph"].map((key)=>button(t(key),()=>{mode=key;render();}));
    modes.append(...buttons);
    const compare = button(t("monthly"),()=>showDetail([...selected]));
    controls.append(modes,compare);
    container.append(node("p",t("note"),"operational-note"));
    if(kind==="application") container.append(node("p",t("appNote"),"operational-note"));
    container.append(controls,notice,output);
    const table = (headers,body) => {
      const wrap=node("div",undefined,"table-wrap operational-table-wrap"), tbl=node("table"), head=node("thead"), tr=node("tr"), tbody=node("tbody");
      headers.forEach((title)=>{const cell=node("th",title);cell.scope="col";tr.append(cell);});head.append(tr);
      body.forEach((cells)=>{const tr=node("tr");cells.forEach((content)=>{const cell=node("td");if(content instanceof Node)cell.append(content);else cell.textContent=content;tr.append(cell);});tbody.append(tr);});
      tbl.append(head,tbody);wrap.append(tbl);return wrap;
    };
    const visibleRows = () => rows.filter((row)=>{
      const cls=model.classify(row,kind);
      return (category.value==="all"||cls.category===category.value) && (group.value==="all"||cls.group===group.value) && (trend.value==="all"||row.trend===trend.value) && (!confidence||confidence.value==="all"||row.inference_confidence===confidence.value);
    }).sort((a,b)=>(b[metric.value==="share"?"current_mapped_job_share_pct":"current_monthly_unique_job_observations"] ?? -1)-(a[metric.value==="share"?"current_mapped_job_share_pct":"current_monthly_unique_job_observations"] ?? -1));
    function nameButton(row) {return button(model.label(row,kind),()=>showDetail([row]),"operational-name");}
    function choose(row) {
      const label=node("label",undefined,"operational-compare-check"), input=node("input");input.type="checkbox";input.checked=selected.has(row);
      input.setAttribute("aria-label",t("compare")+": "+model.label(row,kind));
      input.addEventListener("change",()=>{
        if(input.checked && selected.size>=6){input.checked=false;notice.textContent=t("limit");return;}
        if(input.checked)selected.add(row);else selected.delete(row);
        notice.textContent="";compare.disabled=!selected.size;
      });
      label.append(input);return label;
    }
    function render() {
      output.replaceChildren();
      buttons.forEach((b,i)=>b.setAttribute("aria-pressed",String(mode===["table","graph"][i])));
      compare.disabled=!selected.size;
      const filtered=visibleRows();
      if(!filtered.length){output.append(node("p",t("empty"),"operational-empty"));return;}
      if(mode==="table"){
        output.append(table([t("compare"),t("name"),t("category"),t("count"),t("share"),t("trend"),...(confidence?[t("confidence")]:[])],filtered.map((row)=>[
          choose(row),nameButton(row),categoryLabel(model.classify(row,kind).category),
          format(row.current_monthly_unique_job_observations),format(row.current_mapped_job_share_pct),t(row.trend),...(confidence?[t(row.inference_confidence||"unknown")]:[])
        ])));
      } else {
        const key=metric.value==="share"?"current_mapped_job_share_pct":"current_monthly_unique_job_observations";
        const max=Math.max(1,...filtered.map((row)=>Number.isFinite(row[key])?row[key]:0));
        const chart=node("div",undefined,"operational-bars");chart.setAttribute("aria-label",t(metric.value));
        filtered.forEach((row)=>{
          const item=node("div",undefined,"operational-bar-row"),track=node("span",undefined,"operational-bar-track"),bar=node("span",undefined,"operational-bar");
          bar.style.width=Number.isFinite(row[key])?String(row[key]/max*100)+"%":"0%";track.append(bar);
          track.setAttribute("aria-hidden","true");
          item.append(choose(row),nameButton(row),track,node("span",format(row[key])));
          chart.append(item);
        });output.append(chart);
      }
    }
    function showDetail(detailRows) {
      if(!detailRows.length)return;
      const dialog=node("dialog",undefined,"operational-dialog"), heading=node("h2",t("monthly")), head=node("div",undefined,"operational-dialog-heading");
      heading.id="monthly-"+kind;dialog.setAttribute("aria-labelledby",heading.id);
      const close=button(t("close"),()=>dialog.close());
      head.append(heading,close);
      const toggle=node("div",undefined,"operational-segmented"), plot=node("div");
      toggle.setAttribute("role","group");toggle.setAttribute("aria-label",language==="ja"?"月次表示形式":"Monthly view");
      const metricLabel=node("label",language==="ja"?"指標":"Metric"), detailMetric=node("select");
      [["count",t("jobs")],["share",t("share")]].forEach(([value,label])=>{const option=node("option",label);option.value=value;detailMetric.append(option);});
      detailMetric.value=metric.value;metricLabel.append(detailMetric);
      let view="graph";
      const viewButtons=["graph","table"].map((key)=>button(t(key),()=>{view=key;draw();}));
      toggle.append(...viewButtons);
      dialog.append(head,metricLabel,toggle,node("p",t("monthlyNote"),"operational-note"),plot);
      function draw(){
        plot.replaceChildren();viewButtons.forEach((b,i)=>b.setAttribute("aria-pressed",String(view===["graph","table"][i])));
        const monthly=model.monthlySeries(detailRows,detailMetric.value);
        if(!monthly.months.length){plot.append(node("p",t("empty")));return;}
        if(view==="table"){
          plot.append(table([t("month"),...detailRows.map((row)=>model.label(row,kind))],monthly.months.map((month,i)=>[month.slice(0,7),...monthly.series.map((values)=>format(values[i]))])));
          return;
        }
        const legend=node("ul",undefined,"operational-chart-legend");
        detailRows.forEach((row,i)=>{const li=node("li",model.label(row,kind));li.style.borderLeftColor=colors[i];legend.append(li);});
        const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
        const chartWidth = Math.max(280, Math.min(800, dialog.clientWidth - 44));
        svg.setAttribute("viewBox","0 0 "+chartWidth+" 320");svg.setAttribute("role","img");svg.setAttribute("aria-label",t("monthly")+" · "+(detailMetric.value==="share"?t("share"):t("jobs")));
        svg.classList.add("operational-line-chart");
        const add=(tag,attrs,content)=>{const n=document.createElementNS(svg.namespaceURI,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(content!==undefined)n.textContent=content;svg.append(n);return n;};
        const max=Math.max(1,...monthly.series.flat().filter(Number.isFinite));
        const x=(i)=>75+i*(chartWidth-105)/Math.max(1,monthly.months.length-1),y=(n)=>260-n*225/max;
        [0,0.5,1].forEach((fraction)=>{add("line",{x1:75,x2:chartWidth-30,y1:y(max*fraction),y2:y(max*fraction),stroke:"#d9dfe1"});add("text",{x:68,y:y(max*fraction)+5,"text-anchor":"end","font-size":14,fill:"#39464b"},format(Number((max*fraction).toFixed(1))));});
        [...new Set([0,Math.floor((monthly.months.length-1)/2),monthly.months.length-1])].forEach((i)=>add("text",{x:x(i),y:290,"text-anchor":"middle","font-size":14,fill:"#39464b"},monthly.months[i].slice(0,7)));
        monthly.series.forEach((values,i)=>{
          model.segments(values).forEach((segment)=>add("polyline",{points:segment.map(([j,v])=>x(j)+","+y(v)).join(" "),fill:"none",stroke:colors[i],"stroke-width":2.5,"data-series":i}));
          values.forEach((v,j)=>{if(v!==null){const point=add("circle",{cx:x(j),cy:y(v),r:4,fill:colors[i],"data-value":v});const title=document.createElementNS(svg.namespaceURI,"title");title.textContent=model.label(detailRows[i],kind)+" · "+monthly.months[j]+": "+format(v);point.append(title);}});
        });
        plot.append(legend,svg);
      }
      detailMetric.addEventListener("change",draw);
      window.addEventListener("resize",draw);
      dialog.addEventListener("close",()=>{window.removeEventListener("resize",draw);dialog.remove();},{once:true});
      dialog.addEventListener("click",(event)=>{if(event.target===dialog){const b=dialog.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)dialog.close();}});
      container.append(dialog);dialog.showModal();draw();close.focus();
    }
    controls.querySelectorAll("select").forEach((control)=>control.addEventListener("change",()=>{
      selected.clear();notice.textContent="";render();
    }));
    render();
  }
  window.OpenFSOperationalExplorer = {mount};
})();
