import React from 'react';

export default function PatientGenotypeProfile({ patientProfile, selectedDrug, targetGene }) {
  const profileEntries = Object.entries(patientProfile || {});

  const getStatusBadge = (gene, status) => {
    const st = (status || '').toUpperCase();
    if (st === 'NORMAL') {
      return {
        cardBg: 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300',
        label: 'Normal Metabolizer'
      };
    } else if (st === 'INTERMEDIATE') {
      return {
        cardBg: 'bg-amber-950/20 border-amber-500/40 text-amber-300',
        label: 'Intermediate Metabolizer'
      };
    } else if (st === 'POOR') {
      return {
        cardBg: 'bg-red-950/20 border-red-500/40 text-red-300',
        label: 'Poor Metabolizer'
      };
    } else {
      return {
        cardBg: 'bg-slate-950/60 border-slate-800 text-slate-400',
        label: 'Insufficient Genomic Evidence'
      };
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white tracking-wide">Patient Genotype Profile</h3>
            <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded">
              DETERMINISTIC EVIDENCE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Target Gene Functional Phenotypes Extracted from VCF</p>
        </div>

        <span className="text-xs font-mono text-slate-400">5 PHARMACOGENES PANEL</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {profileEntries.map(([gene, status]) => {
          const style = getStatusBadge(gene, status);
          const isTarget = gene === targetGene;

          return (
            <div 
              key={gene} 
              className={`p-4 rounded-xl border flex flex-col justify-between transition-all ${style.cardBg} ${
                isTarget ? 'ring-2 ring-blue-500/60 shadow-lg scale-[1.02]' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-black text-sm text-white">{gene}</span>
                {isTarget && (
                  <span className="text-[9px] font-mono bg-blue-500/30 text-blue-200 border border-blue-400/40 px-1.5 py-0.5 rounded font-bold uppercase">
                    TARGET
                  </span>
                )}
              </div>

              <span className="text-xs font-extrabold uppercase tracking-wide">
                {style.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
