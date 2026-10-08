import React from 'react';

export default function Header({ currentDoctor, onNavigate, onLogout, activeTab }) {
  if (!currentDoctor) return null;

  // Extract initials for avatar fallback
  const getInitials = (name) => {
    if (!name) return "DR";
    const clean = name.replace(/^dr\.?\s+/i, "");
    const parts = clean.trim().split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
  };

  return (
    <header className="h-20 bg-slate-900/60 border-b border-white/10 flex items-center justify-between px-6 md:px-8 z-30 shrink-0 backdrop-blur-xl">
      {/* BRAND & NAVIGATION */}
      <div className="flex items-center space-x-6">
        <div 
          onClick={() => onNavigate('doctor_dashboard')} 
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.4)] group-hover:scale-105 transition-transform">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <div>
            <h1 className="text-lg font-extrabold text-white tracking-tight flex items-center gap-1.5">
              PharmaGuard <span className="text-xs bg-blue-500/20 text-blue-300 border border-blue-500/30 px-1.5 py-0.5 rounded font-mono">CLINICAL</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-mono">Precision PGx Decision Support</p>
          </div>
        </div>

        {/* NAVIGATION LINKS */}
        <nav className="hidden md:flex items-center space-x-2 pl-6 border-l border-white/10">
          <button
            onClick={() => onNavigate('doctor_dashboard')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'doctor_dashboard'
                ? 'bg-blue-600/30 text-blue-300 border border-blue-500/40 shadow-inner'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('upload')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'upload'
                ? 'bg-blue-600/30 text-blue-300 border border-blue-500/40 shadow-inner'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Analyze Patient
          </button>
        </nav>
      </div>

      {/* DOCTOR PROFILE & LOGOUT */}
      <div className="flex items-center space-x-4">
        {/* DOCTOR INFO BADGE */}
        <div className="flex items-center space-x-3 bg-slate-950/60 px-3.5 py-1.5 rounded-full border border-white/10 shadow-inner">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-blue-600 border border-indigo-400/50 flex items-center justify-center text-xs font-black text-white shadow-sm">
            {getInitials(currentDoctor.name)}
          </div>
          <div className="text-left hidden sm:block">
            <span className="text-xs font-bold text-white block leading-tight">
              {currentDoctor.name.startsWith("Dr.") ? currentDoctor.name : `Dr. ${currentDoctor.name}`}
            </span>
            <span className="text-[10px] text-slate-400 font-mono block leading-tight">
              {currentDoctor.hospital || "Clinical Specialist"}
            </span>
          </div>
        </div>

        {/* LOGOUT BUTTON */}
        <button
          onClick={onLogout}
          className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 hover:border-red-500/50 px-3 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-colors"
          title="Logout of Doctor Portal"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
}
