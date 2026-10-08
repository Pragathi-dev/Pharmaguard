import React from 'react';

export default function PGxRiskModule({ riskObj, pmgrfObj }) {
  const isAvailable = riskObj && riskObj.isAvailable;
  const riskCategory = pmgrfObj?.riskCategory || "Low";
  const score = pmgrfObj?.score ?? 0;
  const contributingFeatures = riskObj?.contributingFeatures || [];
  const reasoning = pmgrfObj?.reason || "Multi-gene evaluation based on CPIC evidence.";

  const getBadgeStyle = (category) => {
    switch (category) {
      case "High":
        return "bg-red-500/20 text-red-300 border-red-500/40";
      case "Moderate":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "Low":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div>
          <h3 className="text-lg font-bold text-white tracking-wide">Pharmacogenomic Clinical Risk Assessment</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Deterministic PGx Risk Tier based on verified genotype variants & CPIC guidelines
          </p>
        </div>

        <span className={`text-xs font-mono px-3 py-1 rounded-full font-bold border ${getBadgeStyle(riskCategory)}`}>
          CLINICAL RISK TIER: {riskCategory.toUpperCase()} RISK
        </span>
      </div>

      {!isAvailable ? (
        <div className="bg-slate-950/70 p-6 rounded-xl border border-slate-800 text-center flex flex-col items-center justify-center min-h-[140px]">
          <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 mb-3 border border-slate-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <span className="text-sm font-bold text-slate-300 mb-1">PGx Risk Evaluation Unavailable</span>
          <p className="text-xs text-slate-400 max-w-md leading-relaxed">
            Risk evaluation is unavailable due to insufficient genomic evidence in the uploaded VCF sample.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          
          {/* RISK TIER DISPLAY */}
          <div className="md:col-span-5 flex flex-col items-center justify-center border-r-0 md:border-r border-white/10 pr-0 md:pr-6">
            <div className="text-center my-2">
              <span className="text-xs font-mono text-slate-400 uppercase block mb-1">Calculated PGx Risk Tier</span>
              <span className={`text-3xl font-black px-4 py-1.5 rounded-xl border inline-block ${getBadgeStyle(riskCategory)}`}>
                {riskCategory} Risk
              </span>
            </div>

            {score !== null && (
              <div className="text-center w-full bg-slate-950/60 rounded-lg p-2.5 border border-white/5 mt-3">
                <span className="text-[10px] font-mono text-blue-400 block mb-0.5">PMGRF COMPOSITE RISK SCORE</span>
                <span className="text-lg font-black text-white">{score} <span className="text-xs text-slate-400 font-normal">/ 15</span></span>
              </div>
            )}
          </div>

          {/* CONTRIBUTING PHENOTYPES & EXPLANATION */}
          <div className="md:col-span-7 space-y-4">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-white/5">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                Actionable PGx Risk Drivers:
              </span>
              {contributingFeatures.length > 0 ? (
                <ul className="space-y-1.5">
                  {contributingFeatures.map((feat, idx) => (
                    <li key={idx} className="text-xs font-semibold text-amber-300 flex items-center gap-2">
                      <span className="text-amber-400">•</span> {feat}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-400 font-medium">
                  • Normal Metabolizer status across evaluated panel. Standard label dosing indicated.
                </p>
              )}
            </div>

            <div className="bg-slate-950/40 p-3.5 rounded-xl border border-blue-500/20 text-xs text-slate-300 leading-relaxed">
              <span className="font-bold text-slate-400 block mb-1">Clinical Rationale:</span>
              {reasoning}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
