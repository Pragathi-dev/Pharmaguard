import React, { useState, useEffect } from 'react';
import { fetchDoctorReports } from '../services/auth';

export default function DoctorDashboard({ currentDoctor, onNavigate, onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    const data = await fetchDoctorReports();
    setReports(data);
    setLoading(false);
  };

  const getRiskBadge = (category) => {
    const cat = (category || 'low').toLowerCase();
    if (cat.includes('high')) return 'bg-red-500/20 text-red-400 border-red-500/40';
    if (cat.includes('moderate')) return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
    return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
  };

  const doctorName = currentDoctor?.name?.startsWith("Dr.")
    ? currentDoctor.name
    : `Dr. ${currentDoctor?.name || "Clinician"}`;

  const distinctSamples = new Set(reports.map(r => r.patient_sample_id)).size;
  const lastLoginTime = new Date().toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short'
  });

  return (
    <div className="relative z-10 flex flex-col w-full flex-1 animate-fade-in backdrop-blur-md bg-slate-950/80 p-4 md:p-10 space-y-8 pb-16">
      <div className="max-w-7xl mx-auto w-full space-y-8">

        
        {/* =========================================
            DOCTOR WELCOME & STATS BANNER
            ========================================= */}
        <div className="bg-gradient-to-r from-slate-900/90 via-slate-900/80 to-blue-950/40 border border-blue-500/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            
            {/* WELCOME TEXT */}
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 px-3 py-1 rounded-full font-bold uppercase tracking-wider">
                  CLINICAL DECISION SUPPORT
                </span>
                <span className="text-xs font-mono text-slate-400">ID: {currentDoctor?.doctor_id || "MD-LOCAL"}</span>
              </div>
              <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
                Welcome {doctorName}
              </h1>
              <p className="text-sm text-slate-400 mt-1 font-medium">
                {currentDoctor?.hospital || "General Hospital"} | Precision Pharmacogenomic Risk Engine
              </p>
            </div>

            {/* ACTION BUTTONS */}
            <div className="flex flex-wrap items-center gap-4">
              <button
                onClick={() => onNavigate('upload')}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-extrabold px-6 py-3.5 rounded-xl shadow-[0_0_25px_rgba(59,130,246,0.4)] transition-all transform hover:scale-105 flex items-center space-x-2 text-sm"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4"></path></svg>
                <span>Analyze New Patient</span>
              </button>

              <a
                href="#reports-section"
                className="bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600 text-slate-200 font-bold px-6 py-3.5 rounded-xl transition-colors text-sm flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span>View Reports</span>
              </a>
            </div>

          </div>

          {/* THREE METRICS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 pt-6 border-t border-white/10">
            
            {/* Total Analyses */}
            <div className="bg-slate-950/60 p-5 rounded-2xl border border-white/5 flex items-center justify-between shadow-inner">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Total Analyses</span>
                <span className="text-3xl font-black text-white">{reports.length}</span>
              </div>
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
              </div>
            </div>

            {/* Recent Patients */}
            <div className="bg-slate-950/60 p-5 rounded-2xl border border-white/5 flex items-center justify-between shadow-inner">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Recent Patients</span>
                <span className="text-3xl font-black text-indigo-400">{distinctSamples}</span>
              </div>
              <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
              </div>
            </div>

            {/* Last Login */}
            <div className="bg-slate-950/60 p-5 rounded-2xl border border-white/5 flex items-center justify-between shadow-inner">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Last Login</span>
                <span className="text-sm font-extrabold text-slate-200">{lastLoginTime}</span>
              </div>
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
            </div>

          </div>
        </div>

        {/* =========================================
            PATIENT REPORT HISTORY SECTION
            ========================================= */}
        <div id="reports-section" className="bg-slate-900/70 border border-blue-500/30 rounded-3xl p-8 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
            <div>
              <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
                Patient Report History
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Historical pharmacogenomic analysis records saved under {doctorName}'s clinical profile.
              </p>
            </div>
            <span className="text-xs font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 px-3 py-1 rounded-full font-bold">
              {reports.length} RECORDS SAVED
            </span>
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-400 font-mono text-sm animate-pulse">
              Loading Patient Report History...
            </div>
          ) : reports.length === 0 ? (
            <div className="p-12 text-center bg-slate-950/60 rounded-2xl border border-white/5">
              <div className="w-16 h-16 bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-blue-400 border border-blue-500/30">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              </div>
              <h3 className="text-lg font-bold text-white mb-1">No Patient Reports Found</h3>
              <p className="text-xs text-slate-400 mb-6 max-w-md mx-auto">
                No genomic evaluations have been run yet for this doctor account. Click below to analyze your first patient VCF file.
              </p>
              <button
                onClick={() => onNavigate('upload')}
                className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2.5 rounded-xl text-xs transition-colors shadow-lg"
              >
                Analyze First Patient VCF
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-xs text-slate-400 uppercase tracking-wider font-mono border-b border-white/10">
                  <tr>
                    <th className="py-3.5 px-4">Report ID</th>
                    <th className="py-3.5 px-4">Sample / Patient ID</th>
                    <th className="py-3.5 px-4">Source VCF</th>
                    <th className="py-3.5 px-4">Risk Category</th>
                    <th className="py-3.5 px-4">Risk Score</th>
                    <th className="py-3.5 px-4">Analysis Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-medium">
                  {reports.map((report, idx) => (
                    <tr key={idx} className="hover:bg-blue-900/20 transition-colors">
                      <td className="py-4 px-4 font-mono font-bold text-blue-400">
                        {report.report_id}
                      </td>
                      <td className="py-4 px-4 font-bold text-white">
                        {report.patient_sample_id}
                      </td>
                      <td className="py-4 px-4 text-xs font-mono text-slate-400">
                        {report.source_file}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`text-xs font-bold uppercase px-3 py-1 rounded-full border ${getRiskBadge(report.risk_category)}`}>
                          {report.risk_category} Risk
                        </span>
                      </td>
                      <td className="py-4 px-4 font-mono font-bold text-slate-200">
                        {report.risk_score}%
                      </td>
                      <td className="py-4 px-4 text-xs text-slate-400">
                        {new Date(report.analysis_date).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
