import React from 'react';

export default function ClinicalSummaryCard({ executiveSummary, isInsufficient }) {
  const { actionableFindings, evidenceStatus, clinicalRecStatus, riskAssessmentStatus } = executiveSummary;

  return (
    <div className={`rounded-2xl p-6 shadow-xl border backdrop-blur-xl transition-all ${
      isInsufficient
        ? 'bg-slate-900/90 border-slate-700 shadow-slate-950/50'
        : 'bg-gradient-to-r from-slate-900/95 via-slate-900/90 to-blue-950/50 border-blue-500/40 shadow-blue-950/40'
    }`}>
      
      {/* CARD HEADER */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
            isInsufficient ? 'bg-slate-800 text-slate-300' : 'bg-blue-600/30 text-blue-300 border border-blue-500/40'
          }`}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          </div>
          <div>
            <h2 className="text-xl font-black text-white tracking-tight">Clinical Summary</h2>
            <p className="text-xs text-slate-400">Executive Case Briefing for Physician Review</p>
          </div>
        </div>

        <span className={`text-xs font-mono font-bold px-3 py-1 rounded-full border ${
          isInsufficient 
            ? 'bg-slate-800 text-slate-300 border-slate-600' 
            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
        }`}>
          {isInsufficient ? 'EVIDENCE INSUFFICIENT' : 'PANEL EVALUATED'}
        </span>
      </div>

      {/* 4-COLUMN SUMMARY GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* 1. ACTIONABLE FINDINGS */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-white/5 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            Actionable Findings:
          </span>
          <div className="flex-1">
            {actionableFindings.length === 1 && actionableFindings[0] === 'None' ? (
              <span className="text-sm font-extrabold text-slate-300">None</span>
            ) : (
              <ul className="space-y-1">
                {actionableFindings.map((finding, idx) => (
                  <li key={idx} className="text-xs font-bold text-amber-300 flex items-start gap-1.5">
                    <span className="text-amber-400 mt-0.5">•</span> {finding}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* 2. EVIDENCE STATUS */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-white/5 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            Evidence Status:
          </span>
          <span className={`text-xs font-bold leading-relaxed ${
            isInsufficient ? 'text-slate-400 font-mono' : 'text-emerald-300 font-mono'
          }`}>
            {evidenceStatus}
          </span>
        </div>

        {/* 3. CPIC RECOMMENDATION STATUS */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-white/5 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            CPIC Recommendation:
          </span>
          <span className={`text-xs font-extrabold uppercase px-2.5 py-1 rounded-md inline-block border w-fit ${
            clinicalRecStatus === 'Not Determinable'
              ? 'bg-slate-800 text-slate-300 border-slate-700'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
          }`}>
            {clinicalRecStatus}
          </span>
        </div>

        {/* 4. RISK ASSESSMENT */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-white/5 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            Risk Assessment:
          </span>
          <span className={`text-xs font-bold leading-relaxed ${
            isInsufficient ? 'text-slate-400 italic' : 'text-blue-300'
          }`}>
            {riskAssessmentStatus}
          </span>
        </div>

      </div>
    </div>
  );
}
