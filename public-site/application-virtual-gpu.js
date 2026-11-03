/* Exact browser implementation of application_typed_kernel_model.py v1.
   Source-only hypotheses; no target timing, fitting or upload. */
((scope) => {
  "use strict";
  const counters = ["fp64_ops", "fp32_ops", "hbm_bytes", "l2_bytes", "profiled_nanoseconds"];
  const positive = v => typeof v === "number" && Number.isFinite(v) && v > 0;
  const nonnegative = v => typeof v === "number" && Number.isFinite(v) && v >= 0;
  const median = values => {const s = [...values].sort((a,b)=>a-b); return (s[Math.floor((s.length-1)/2)]+s[Math.floor(s.length/2)])/2;};
  function validateSpec(spec) {
    if (!positive(spec.bandwidth)) throw Error("HBM bandwidth must be finite and >0 GB/s");
    for (const key of ["fp64", "fp32"]) if (spec[key] !== null && !positive(spec[key])) throw Error(key+" must be finite and >0 TFLOP/s, or unknown");
  }
  function roof(sample, spec) {
    let compute = 0;
    for (const [work, peak] of [["fp64_ops","fp64"],["fp32_ops","fp32"]]) {
      if (!nonnegative(sample[work])) throw Error("Invalid "+work);
      if (sample[work] > 0) {
        if (!positive(spec[peak])) throw Error("Positive "+work+" requires known "+peak+" peak");
        const denominator=spec[peak]*1e12;
        if(!positive(denominator)) throw Error("Peak outside finite arithmetic range");
        compute += sample[work]/denominator;
      }
    }
    const denominator=spec.bandwidth*1e9;
    if(!positive(denominator)) throw Error("Bandwidth outside finite arithmetic range");
    const memory=sample.hbm_bytes/denominator;
    if(!nonnegative(compute)||!nonnegative(memory)) throw Error("Specification outside finite arithmetic range");
    return {seconds:Math.max(compute,memory),compute_seconds:compute,memory_seconds:memory};
  }
  function predict(basis, targetSpec) {
    validateSpec(basis.baseline_spec); validateSpec(targetSpec);
    const d=basis.data;
    if (JSON.stringify(d.runs.map(r=>r.warmup)) !== "[true,false,false,false]") throw Error("Normal repetition policy");
    if (d.runs.some(r=>!nonnegative(r.seconds)) || !positive(d.window_seconds)) throw Error("Invalid normal timing");
    const t0=median(d.runs.slice(1).map(r=>r.seconds)), window=d.window_seconds;
    if (!positive(t0)) throw Error("Invalid normal median");
    if (Object.values(d.timeline).some(v=>!nonnegative(v)) || Math.abs(Object.values(d.timeline).reduce((a,b)=>a+b,0)-window)>1e-7) throw Error("Exclusive timeline mismatch");
    const gpuSum=d.kernels.reduce((a,k)=>a+k.seconds,0);
    if (Math.abs(gpuSum-d.timeline.gpu)>1e-6) throw Error("Overlapping kernels require another model");
    let total=0, alternate=0,covered=0; const steps=[];
    for (const k of d.kernels) {
      if (!nonnegative(k.seconds)) throw Error("Invalid kernel time");
      const valid=k.samples.filter(s=>counters.every(c=>s[c]!==null && s[c]!==undefined));
      const old=k.seconds*t0/window;
      if (!valid.length) {total+=old;alternate+=old;steps.push({kernel:k.name,status:"uncovered-held-constant",baseline_seconds:old,predicted_seconds:old});continue;}
      if (valid.some(s=>counters.some(c=>!nonnegative(s[c])))) throw Error("Invalid counter work");
      const sample=Object.fromEntries(counters.map(c=>[c,median(valid.map(s=>s[c]))]));
      const duration=sample.profiled_nanoseconds/1e9;
      if (!positive(duration)) throw Error("Invalid counter duration");
      const source=roof(sample,basis.baseline_spec),target=roof(sample,targetSpec);
      const residual=Math.max(0,duration-source.seconds);
      const ratio=source.seconds<=duration?(residual+target.seconds)/duration:Math.max(1,target.seconds/source.seconds);
      const alternateRatio=source.seconds?target.seconds/source.seconds:1;
      total+=old*ratio;alternate+=old*alternateRatio;covered+=k.seconds;
      steps.push({kernel:k.name,status:"sampled",sample,duration_seconds:duration,source_roof:source,target_roof:target,
        residual_seconds:residual,baseline_seconds:old,scaling_ratio:ratio,alternate_ratio:alternateRatio,predicted_seconds:old*ratio});
    }
    const fixed=Object.entries(d.timeline).filter(([k])=>k!=="gpu").reduce((a,[,v])=>a+v*t0/window,0);
    const ratio=basis.phases.compute/t0, fixedPhases=basis.phases.initialization+basis.phases.finalization;
    const seconds=(total+fixed)*ratio+fixedPhases;
    if(!positive(seconds)) throw Error("Result outside finite positive arithmetic range");
    return {seconds,
      minimum:(Math.min(total,alternate)+.5*fixed)*ratio+.5*fixedPhases,
      maximum:(Math.max(total,alternate)+2*fixed)*ratio+2*fixedPhases,
      baseline_seconds:basis.phases.total,coverage_fraction:gpuSum?covered/gpuSum:0,
      arithmetic:{normal_compute_median_seconds:t0,trace_window_seconds:window,kernels:steps,
        held_non_gpu_seconds:fixed,phase_ratio:ratio,initialization_seconds:basis.phases.initialization,
        finalization_seconds:basis.phases.finalization,kernel_sum_seconds:total,
        final_expression:"(kernel_sum_seconds + held_non_gpu_seconds) * phase_ratio + initialization_seconds + finalization_seconds"}};
  }
  const api={predict,validateSpec,roof};
  if (typeof module !== "undefined" && module.exports) module.exports=api;
  scope.OpenFSVirtualGPU=api;
})(typeof window !== "undefined" ? window : globalThis);
