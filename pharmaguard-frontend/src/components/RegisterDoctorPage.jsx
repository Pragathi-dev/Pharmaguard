import React, { useState } from 'react';
import { registerDoctor } from '../services/auth';

export default function RegisterDoctorPage({ onRegisterSuccess, onNavigateLogin, onSwitchToLogin }) {
  const handleSwitchLogin = onNavigateLogin || onSwitchToLogin;

  const [formData, setFormData] = useState({
    name: '',
    doctor_id: '',
    hospital: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (
      !formData.name ||
      !formData.doctor_id ||
      !formData.hospital ||
      !formData.email ||
      !formData.password
    ) {
      setError('Please fill in all medical registration fields.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match. Please re-enter your password.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);
    try {
      const data = await registerDoctor({
        name: formData.name,
        doctor_id: formData.doctor_id,
        hospital: formData.hospital,
        email: formData.email,
        password: formData.password
      });
      setLoading(false);
      if (onRegisterSuccess) {
        onRegisterSuccess(data.doctor);
      }
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="relative z-10 flex flex-col items-center justify-center w-full h-full px-4 py-8 overflow-y-auto backdrop-blur-md bg-slate-950/75 animate-fade-in">
      
      {/* GLOWING BACKGROUND CIRCLE */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/20 rounded-full blur-[100px] pointer-events-none"></div>

      {/* REGISTER CARD */}
      <div className="w-full max-w-lg bg-slate-900/90 border border-blue-500/30 rounded-3xl p-8 shadow-[0_0_50px_rgba(0,0,0,0.6)] backdrop-blur-2xl relative z-10 my-auto">
        
        {/* BRANDING HEADER */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-[0_0_30px_rgba(59,130,246,0.5)]">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">PharmaGuard AI</h1>
          <p className="text-xs text-blue-300/80 font-mono mt-0.5 uppercase tracking-wider">Doctor Portal Registration</p>
        </div>

        <div className="border-t border-white/10 pt-5 mb-4">
          <h2 className="text-base font-bold text-slate-100 text-center mb-1">Create Doctor Account</h2>
          <p className="text-xs text-slate-400 text-center mb-5">Register your medical profile to enable personalized pharmacogenomic decision support.</p>

          {/* ERROR ALERT */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-xl mb-4 text-xs font-semibold text-red-300 text-center flex items-center justify-center gap-2">
              <span>⚠️</span> {error}
            </div>
          )}

          {/* REGISTER FORM */}
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Dr. Jane Smith"
                required
                className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Doctor ID / Reg No.</label>
                <input
                  type="text"
                  name="doctor_id"
                  value={formData.doctor_id}
                  onChange={handleChange}
                  placeholder="MD-884920"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Hospital Name</label>
                <input
                  type="text"
                  name="hospital"
                  value={formData.hospital}
                  onChange={handleChange}
                  placeholder="St. Jude Medical Center"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Medical Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="dr.smith@hospital.org"
                required
                className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Password</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1 uppercase tracking-wider">Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-blue-500 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none transition-colors shadow-inner"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-[0_0_25px_rgba(59,130,246,0.4)] transition-all transform hover:scale-[1.02] active:scale-[0.98] text-sm mt-3 disabled:opacity-50"
            >
              {loading ? "Registering Profile..." : "Create Account"}
            </button>
          </form>
        </div>

        {/* SWITCH TO LOGIN LINK */}
        <div className="text-center pt-2 border-t border-white/5">
          <button
            onClick={handleSwitchLogin}
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
          >
            Already registered? <span className="underline font-bold">Sign In to Doctor Portal</span>
          </button>
        </div>


      </div>
    </div>
  );
}
