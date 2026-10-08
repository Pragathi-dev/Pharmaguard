import React from 'react';

export default function AIRiskModule({ aiRiskObj }) {
  const {
    isAvailable,
    riskScore,
    confidence,
    interval,
    reasoningTrace,
    contributingFeatures,
    modelVersion
  } = aiRiskObj;

  return (
    <div className="bg-slate-900/80 border border-blue-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-xl">
      <div className="absolute top-0 right-0 bg-blue-500/20 text-blue-300 text-[10px] font-bold px-3 py-1 rounded-bl-lg font-mono">
        EXPLORATORY ML MODEL
      </div>

      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-slate-200 font-bold uppercase tracking-wider text-xs">AI Risk Prediction Module</h3>
        <span className="text-[10px] text-slate-400 font-mono">({modelVersion})</span>
      </div>

      {!isAvailable ? (
        /* HIDE DIAL GAUGE COMPLETELY & DISPLAY CLEAR WARNING */
        <div className="bg-slate-950/70 p-6 rounded-xl border border-slate-800 text-center flex flex-col items-center justify-center min-h-[160px]">
          <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 mb-3 border border-slate-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <span className="text-sm font-bold text-slate-300 mb-1">AI Prediction Unavailable</span>
          <p className="text-xs text-slate-400 max-w-md leading-relaxed">
            AI prediction unavailable due to insufficient genomic evidence. The CatBoost ML regressor requires verified feature inputs.
          </p>
        </div>
      ) : (
        /* DISPLAY VALID AI RISK SCORE GAUGE & SPECIFIC CONTRIBUTING FEATURES */
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          
          {/* DIAL GAUGE & CONFIDENCE */}
          <div className="md:col-span-5 flex flex-col items-center justify-center border-r-0 md:border-r border-white/10 pr-0 md:pr-6">
            <div className="relative w-36 h-36 my-2">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1e293b" strokeWidth="8" />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke={riskScore > 60 ? "#ef4444" : riskScore > 30 ? "#eab308" : "#10b981"}
                  strokeWidth="8"
                  strokeDasharray="251"
                  strokeDashoffset={251 - (251 * ((riskScore || 0) / 100))}
                  className="drop-shadow-[0_0_10px_rgba(59,130,246,0.5)] transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-black text-white">{riskScore}<span className="text-lg text-slate-400">%</span></span>
                <span className="text-[9px] font-mono text-slate-400 uppercase">Predicted Risk</span>
              </div>
            </div>

            <div className="text-center w-full bg-slate-950/60 rounded-lg p-2.5 border border-white/5 mt-2">
              <span className="text-[10px] font-mono text-blue-400 block mb-1">STATISTICAL CONFORMAL BOUNDS</span>
              <span className="bg-blue-900/30 text-blue-300 text-xs font-bold px-2 py-0.5 rounded border border-blue-700/50 inline-block mb-1">
                {confidence}
              </span>
              <p className="text-[11px] font-mono text-slate-400">
                Interval: [{interval[0]} - {interval[1]}]
              </p>
            </div>
          </div>

          {/* CONTRIBUTING FEATURES & REASONING TRACE */}
          <div className="md:col-span-7 space-y-4">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-white/5">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                Contributing Genomic Features:
              </span>
              <ul className="space-y-1.5">
                {contributingFeatures.map((feat, idx) => (
                  <li key={idx} className="text-xs font-semibold text-amber-300 flex items-center gap-2">
                    <span className="text-amber-400">•</span> {feat}
                  </li>
                ))}
              </ul>
            </div>

            {reasoningTrace && (
              <div className="bg-slate-950/40 p-3.5 rounded-xl border border-blue-500/20 text-xs text-slate-300 leading-relaxed">
                <span className="font-bold text-slate-400 block mb-1">Reasoning Trace:</span>
                {reasoningTrace}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
