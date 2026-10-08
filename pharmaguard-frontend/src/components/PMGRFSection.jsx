import React from 'react';

export default function PMGRFSection({ pmgrfObj }) {
  const { status, riskCategory, score, contributingCount, reason, contributingGenes } = pmgrfObj;
  const isNotComputable = status === "Not Computable";

  const getRiskCategoryBadge = (category) => {
    const cat = (category || '').toLowerCase();
    if (cat.includes('high')) return 'bg-red-500/20 text-red-400 border-red-500/40';
    if (cat.includes('moderate')) return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
    if (cat.includes('insufficient')) return 'bg-slate-800 text-slate-400 border-slate-700';
    return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  };

  return (
    <div className="bg-gradient-to-r from-slate-900/90 via-slate-900/80 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-xl">
      
      {/* SECTION HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-4 border-b border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-indigo-600/20 border border-indigo-500/40 rounded-xl flex items-center justify-center text-indigo-400 shadow-inner">
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white tracking-wide">PMGRF Framework Assessment</h3>
              <span className="text-[10px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded">RESEARCH LAYER</span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">PharmaGuard Multi-Gene Risk Framework & Phenotype Aggregation</p>
          </div>
        </div>

        {/* METRICS ROW */}
        <div className="grid grid-cols-3 gap-4 w-full md:w-auto">
          
          {/* PMGRF Status / Score */}
          <div className="bg-slate-950/70 p-3.5 rounded-xl border border-white/5 text-center min-w-[120px]">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">PMGRF Status</span>
            <span className={`text-xl font-black ${isNotComputable ? 'text-slate-400 text-sm font-mono' : 'text-white text-2xl'}`}>
              {isNotComputable ? 'Not Computable' : score}
            </span>
          </div>

          {/* Risk Category */}
          <div className="bg-slate-950/70 p-3.5 rounded-xl border border-white/5 text-center min-w-[140px] flex flex-col items-center justify-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Risk Category</span>
            <span className={`text-[11px] font-black uppercase px-2.5 py-0.5 rounded-full border ${getRiskCategoryBadge(riskCategory)}`}>
              {riskCategory}
            </span>
          </div>

          {/* Contributing Genes */}
          <div className="bg-slate-950/70 p-3.5 rounded-xl border border-white/5 text-center min-w-[120px]">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Contributing Genes</span>
            <span className="text-2xl font-black text-indigo-400">{contributingCount}</span>
          </div>

        </div>
      </div>

      {/* RATIONALE & DETAILS */}
      <div className="mt-4">
        {isNotComputable ? (
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-start gap-3">
            <span className="text-amber-400 text-base">⚠️</span>
            <div>
              <span className="font-bold text-amber-200 block mb-0.5">PMGRF Multi-Gene Risk Calculation Bypassed</span>
              <p className="text-slate-400 leading-relaxed">{reason}</p>
            </div>
          </div>
        ) : (
          <div className="bg-slate-950/80 p-4 rounded-xl border border-white/5 text-xs text-slate-300 leading-relaxed">
            <span className="font-bold text-slate-400 block mb-1">PMGRF Assessment Rationale:</span>
            {reason}
          </div>
        )}
      </div>

    </div>
  );
}
