import React from 'react';
import { availableDrugs, drugGeneMap } from '../services/interpretationEngine';

export default function DrugRecommendationPanel({ selectedDrug, onSelectDrug, recommendationObj }) {
  const {
    drugName,
    associatedGene,
    phenotype,
    riskLevel,
    recommendationStatement,
    rationale,
    patientEvidenceStatus,
    guidelineSource
  } = recommendationObj;

  const isInsufficient = patientEvidenceStatus.includes("Insufficient");

  const getRiskBadgeColor = (level) => {
    const l = (level || '').toLowerCase();
    if (l.includes('high')) return 'bg-red-500/20 text-red-400 border-red-500/40';
    if (l.includes('moderate') || l.includes('caution')) return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
    if (l.includes('insufficient')) return 'bg-slate-800 text-slate-300 border-slate-700';
    return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  };

  return (
    <div className="bg-slate-900/80 border border-blue-500/40 rounded-2xl p-7 shadow-2xl backdrop-blur-xl">
      
      {/* GLOBAL DRUG SELECTOR HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-black text-white tracking-tight">
              Drug Recommendation Panel
            </h2>
            <span className="text-xs font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 px-3 py-0.5 rounded font-bold uppercase">
              Primary Decision Support
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Select therapeutic agent to update recommendations, guidelines, and gene evidence across the report.
          </p>
        </div>

        {/* SINGLE GLOBAL DRUG SELECTOR */}
        <div className="flex items-center gap-3 bg-slate-950/90 px-4 py-2.5 rounded-xl border border-blue-500/50 shadow-inner shrink-0">
          <label htmlFor="global-drug-select" className="text-xs font-extrabold text-blue-300 uppercase tracking-wider whitespace-nowrap">
            Select Target Drug:
          </label>
          <select
            id="global-drug-select"
            value={selectedDrug}
            onChange={(e) => onSelectDrug(e.target.value)}
            className="bg-transparent text-sm font-black text-white focus:outline-none cursor-pointer pr-2"
          >
            {availableDrugs.map(drug => (
              <option key={drug} value={drug} className="bg-slate-900 text-white font-medium">
                {drug} ({drugGeneMap[drug] || "Gene"})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* RECOMMENDED CARD BODY */}
      <div className="mt-6">
        <div
          key={selectedDrug}
          className={`p-6 rounded-2xl border transition-all duration-300 animate-fade-in ${
            isInsufficient
              ? 'bg-slate-950/80 border-slate-700 shadow-inner'
              : riskLevel.toLowerCase().includes('high')
              ? 'bg-gradient-to-b from-red-950/40 to-slate-950/90 border-red-500/40 shadow-[0_0_30px_rgba(239,68,68,0.15)]'
              : 'bg-gradient-to-b from-emerald-950/30 to-slate-950/90 border-emerald-500/40 shadow-[0_0_30px_rgba(16,185,129,0.15)]'
          }`}
        >
          
          {/* HEADER: DRUG, GENE, PHENOTYPE, EVIDENCE STATUS */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-2xl font-black text-white tracking-tight">
                {drugName}
              </span>

              <span className="text-xs font-mono bg-slate-800/90 text-slate-300 border border-slate-700 px-3 py-1 rounded-full">
                Associated Gene: <strong className="text-blue-400 font-bold">{associatedGene}</strong>
              </span>

              <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
                phenotype === 'Unknown' ? 'bg-slate-800 text-slate-400 border-slate-600' : 'bg-white/10 text-white border-white/20'
              }`}>
                Phenotype: <strong className={phenotype === 'Unknown' ? 'text-slate-400' : 'text-emerald-300'}>{phenotype}</strong>
              </span>
            </div>

            <div className="flex items-center gap-3">
              <span className={`text-xs font-mono font-bold px-3 py-1 rounded-full border ${
                isInsufficient ? 'bg-slate-800 text-slate-400 border-slate-600' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
              }`}>
                {patientEvidenceStatus}
              </span>

              <span className={`text-xs font-black uppercase px-3.5 py-1 rounded-full border ${getRiskBadgeColor(riskLevel)}`}>
                {riskLevel} {riskLevel.toLowerCase().includes('risk') || isInsufficient ? '' : 'Risk'}
              </span>
            </div>
          </div>

          {/* CPIC RECOMMENDATION */}
          <div className={`p-5 rounded-xl border mb-5 ${
            isInsufficient 
              ? 'bg-slate-900/90 border-slate-700' 
              : 'bg-blue-950/40 border-blue-500/30'
          }`}>
            <span className="text-xs font-bold text-blue-400 uppercase tracking-wider block mb-2">
              CPIC Recommendation:
            </span>

            {isInsufficient ? (
              <div className="flex items-start gap-3">
                <span className="text-amber-400 text-lg">⚠️</span>
                <div>
                  <p className="text-sm font-extrabold text-amber-200">
                    {recommendationStatement}
                  </p>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Standard CPIC dosing guidelines cannot be deterministically computed without verified genotype calls for {associatedGene}.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-base font-bold text-slate-100 leading-relaxed">
                {recommendationStatement}
              </p>
            )}
          </div>

          {/* CLINICAL RATIONALE */}
          <div className="bg-slate-950/60 p-5 rounded-xl border border-white/5 mb-5 leading-relaxed">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">
              Clinical Rationale:
            </span>
            <p className="text-sm text-slate-300 font-normal leading-relaxed">
              {rationale}
            </p>
          </div>

          {/* GUIDELINE SOURCE */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs text-slate-400 pt-4 border-t border-white/10 gap-2">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-400 uppercase tracking-wider">Guideline Source:</span>
              <span className="text-slate-200 font-medium">{guidelineSource}</span>
            </div>

            <span className="text-[11px] font-mono text-indigo-300 bg-indigo-950/50 border border-indigo-500/30 px-2.5 py-0.5 rounded">
              Verified CPIC Guideline
            </span>
          </div>

        </div>
      </div>

    </div>
  );
}
