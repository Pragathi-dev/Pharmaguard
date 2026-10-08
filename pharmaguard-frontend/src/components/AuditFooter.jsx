import React from 'react';

export default function AuditFooter({ analysisTimestamp }) {
  const formattedTime = analysisTimestamp
    ? new Date(analysisTimestamp).toUTCString()
    : new Date().toUTCString();

  return (
    <footer className="mt-8 pt-6 border-t border-slate-800 text-slate-400 text-xs font-mono">
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        
        <div className="flex flex-wrap items-center gap-6">
          <div>
            <span className="text-slate-400 block text-[10px]">CPIC VERSION</span>
            <strong className="text-slate-200">2025.2 (GRCh37)</strong>
          </div>

          <div>
            <span className="text-slate-400 block text-[10px]">KNOWLEDGE BASE</span>
            <strong className="text-slate-200">v5.2 Verified</strong>
          </div>

          <div>
            <span className="text-slate-400 block text-[10px]">PIPELINE VERSION</span>
            <strong className="text-blue-400">PharmaGuard v3.1</strong>
          </div>
        </div>

        <div className="text-right">
          <span className="text-slate-400 block text-[10px]">ANALYSIS TIMESTAMP (UTC)</span>
          <strong className="text-slate-300">{formattedTime}</strong>
        </div>

      </div>

      <div className="text-center text-[11px] text-slate-400 mt-4 leading-relaxed">
        PharmaGuard Precision Pharmacogenomics Clinical Decision Support System. Standard CPIC dosing guidelines are provided for clinical decision support. Always verify patient medical history prior to prescribing.
      </div>
    </footer>
  );
}
