import React, { useState } from 'react';
import { loginDoctor } from '../services/auth';

export default function LoginPage({ onLoginSuccess, onNavigateRegister, onSwitchToRegister }) {
  const handleSwitchRegister = onNavigateRegister || onSwitchToRegister;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please enter your medical email and password.');
      return;
    }

    setLoading(true);
    try {
      const data = await loginDoctor(email, password);
      setLoading(false);
      if (onLoginSuccess) {
        onLoginSuccess(data.doctor);
      }
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="relative z-10 flex flex-col items-center justify-center w-full h-full px-4 backdrop-blur-md bg-slate-950/75 animate-fade-in">
      
      {/* GLOWING BACKGROUND CIRCLE */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none"></div>

      {/* LOGIN CARD */}
      <div className="w-full max-w-md bg-slate-900/90 border border-blue-500/30 rounded-3xl p-8 shadow-[0_0_50px_rgba(0,0,0,0.6)] backdrop-blur-2xl relative z-10">
        
        {/* BRANDING HEADER */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-[0_0_30px_rgba(59,130,246,0.5)]">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">PharmaGuard AI</h1>
          <p className="text-xs text-blue-300/80 font-mono mt-1 uppercase tracking-wider">Precision Pharmacogenomics Portal</p>
        </div>

        <div className="border-t border-white/10 pt-6 mb-6">
          <h2 className="text-lg font-bold text-slate-100 text-center mb-1">Doctor Login</h2>
          <p className="text-xs text-slate-400 text-center mb-6">Enter your clinical credentials to access patient risk decision tools.</p>

          {/* ERROR ALERT */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-xl mb-4 text-xs font-semibold text-red-300 text-center flex items-center justify-center gap-2">
              <span>⚠️</span> {error}
            </div>
          )}

          {/* LOGIN FORM */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1.5 uppercase tracking-wider">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="dr.smith@hospital.org"
                required
                className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition-colors shadow-inner"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1.5 uppercase tracking-wider">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
                className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition-colors shadow-inner"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-[0_0_25px_rgba(59,130,246,0.4)] transition-all transform hover:scale-[1.02] active:scale-[0.98] text-sm mt-2 disabled:opacity-50"
            >
              {loading ? "Authenticating Doctor..." : "Login"}
            </button>
          </form>
        </div>

        {/* CREATE ACCOUNT LINK */}
        <div className="text-center pt-2 border-t border-white/5">
          <button
            onClick={handleSwitchRegister}
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
          >
            Don't have an account? <span className="underline font-bold">Create Account</span>
          </button>
        </div>


      </div>
    </div>
  );
}
