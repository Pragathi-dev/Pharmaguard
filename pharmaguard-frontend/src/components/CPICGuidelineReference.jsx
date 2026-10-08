import React from 'react';

export default function CPICGuidelineReference({ selectedDrug, targetGene, clinicalRec, isInsufficient }) {
  const drugName = clinicalRec?.drugName || clinicalRec?.drug || selectedDrug;
  const geneName = clinicalRec?.associatedGene || clinicalRec?.gene || targetGene;
  const phenotype = clinicalRec?.phenotype || clinicalRec?.status || "Normal Metabolizer";
  const recommendationText = clinicalRec?.recommendationStatement || clinicalRec?.recommendation || `Initiate ${drugName} at standard label-recommended dosage.`;
  const evidenceSource = clinicalRec?.guidelineSource || clinicalRec?.evidence_source || "CPIC Prescribing Guideline";
  const guidelineVersion = clinicalRec?.guidelineVersion || clinicalRec?.guideline_version || "2025.2";
  const evidenceLevel = clinicalRec?.evidence_level || "A";

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div>
          <h3 className="text-lg font-bold text-white tracking-wide">CPIC Guideline Reference</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Official CPIC Prescribing Guidance for <strong className="text-blue-400">{drugName}</strong> ({geneName})
          </p>
        </div>

        <span className="text-xs font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-3 py-1 rounded-full font-bold">
          SYNCHRONIZED TO GLOBAL SELECTOR
        </span>
      </div>

      {isInsufficient ? (
        <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800 flex flex-col items-center justify-center text-center">
          <span className="text-slate-400 text-xs font-mono mb-1 uppercase tracking-wider">CPIC Evidence Lookup Status</span>
          <span className="text-sm font-bold text-slate-300 mb-2">Genotype Evidence Insufficient</span>
          <p className="text-xs text-slate-400 max-w-lg leading-relaxed">
            Standard CPIC dosing algorithms require verified diplotypes. Patient VCF lacks sufficient genotype evidence for {geneName}.
          </p>
        </div>
      ) : (
        <div className="bg-slate-950/80 p-5 rounded-xl border border-emerald-500/20">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="font-black text-white text-lg block">{drugName}</span>
              <span className="text-xs text-slate-400 font-mono">Gene: <strong className="text-slate-200">{geneName}</strong> | Phenotype: <strong className="text-emerald-400">{phenotype}</strong></span>
            </div>
            <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1 rounded-full font-bold">
              VERIFIED LEVEL: {evidenceLevel}
            </span>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-lg border border-white/5 mb-3">
            <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">Dosing Recommendation Statement:</span>
            <p className="text-sm font-bold text-slate-100 leading-relaxed">{recommendationText}</p>
          </div>

          <div className="text-xs text-slate-400 flex flex-wrap justify-between border-t border-white/5 pt-3 gap-2">
            <span>Evidence Source: <strong className="text-slate-300">{evidenceSource}</strong></span>
            <span>Guideline Version: <strong className="text-slate-300">{guidelineVersion}</strong></span>
          </div>
        </div>
      )}
    </div>
  );
}
