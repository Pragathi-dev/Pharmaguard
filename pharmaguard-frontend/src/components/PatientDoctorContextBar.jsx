import React from 'react';

export default function PatientDoctorContextBar({ currentDoctor, sampleId, analysisDate, onBackToDashboard, onAnalyzeNew }) {
  const formattedDate = analysisDate 
    ? new Date(analysisDate).toISOString().split('T')[0]
    : new Date().toISOString().split('T')[0];

  const doctorName = currentDoctor?.name?.startsWith("Dr.") 
    ? currentDoctor.name 
    : `Dr. ${currentDoctor?.name || "Clinician"}`;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg backdrop-blur-xl">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        
        {/* PATIENT CONTEXT METADATA */}
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="font-mono text-slate-400 font-bold uppercase">PATIENT:</span>
            <strong className="text-white font-mono text-sm">{sampleId || "UNKNOWN"}</strong>
          </div>

          <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="font-mono text-slate-400 font-bold uppercase">ANALYSIS DATE:</span>
            <strong className="text-slate-200 font-mono">{formattedDate}</strong>
          </div>

          <div className="flex items-center gap-2 bg-blue-950/50 px-3 py-1.5 rounded-lg border border-blue-500/30 text-blue-300 font-mono">
            <span className="font-bold">PIPELINE:</span>
            <span>PharmaGuard v3.1</span>
          </div>

          <div className="flex items-center gap-2 bg-emerald-950/40 px-3 py-1.5 rounded-lg border border-emerald-500/30 text-emerald-400 font-mono">
            <span className="font-bold">REPORT VER:</span>
            <span>v3.1-Clinical</span>
          </div>
        </div>

        {/* DOCTOR CONTEXT & ACTIONS */}
        <div className="flex items-center justify-between lg:justify-end gap-4 border-t lg:border-t-0 border-white/10 pt-3 lg:pt-0">
          
          <div className="text-right hidden sm:block">
            <span className="text-xs font-bold text-white block">{doctorName}</span>
            <span className="text-[10px] text-slate-400 font-mono block">
              ID: {currentDoctor?.doctor_id || "MD-LOCAL"} | {currentDoctor?.hospital || "General Hospital"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {onBackToDashboard && (
              <button
                onClick={onBackToDashboard}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
              >
                Dashboard
              </button>
            )}
            {onAnalyzeNew && (
              <button
                onClick={onAnalyzeNew}
                className="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold shadow-md transition-colors"
              >
                Analyze New Patient
              </button>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
