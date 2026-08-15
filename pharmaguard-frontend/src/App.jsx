import React, { useState } from 'react';

function App() {
  const [appState, setAppState] = useState('landing');
  const [loadingStep, setLoadingStep] = useState(0);
  
  // State to hold the actual data coming from Python
  const [analysisResults, setAnalysisResults] = useState(null);

  const loadingMessages = [
    "Extracting Variants from VCF...",
    "Mapping Genes to Phenotypes...",
    "Analyzing Multi-Gene Interactions...",
    "Calculating Probabilistic Risk Score...",
    "Generating Explainability Matrix..."
  ];

  // The function that sends the file to your Python backend
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Start the loading screen
    setAppState('processing');
    setLoadingStep(0);

    // Fake the loading progress for visual effect
    const animationInterval = setInterval(() => {
      setLoadingStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 800);

    // Prepare the file to be sent
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Talk to your Python FastAPI Server
      const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      setAnalysisResults(data); // Save the AI results!

      // Transition to Dashboard once animation completes
      setTimeout(() => {
        clearInterval(animationInterval);
        setAppState('dashboard');
      }, 4000);

    } catch (error) {
      console.error("Error connecting to backend:", error);
      alert("Failed to connect to the Python backend. Is uvicorn running?");
      clearInterval(animationInterval);
      setAppState('upload');
    }
  };

  return (
    <div className="relative flex h-screen w-full overflow-hidden font-sans text-slate-100 bg-slate-950">
      
      {/* BACKGROUND VIDEO */}
      <video autoPlay loop muted playsInline className="absolute inset-0 w-full h-full object-cover z-0 opacity-30 mix-blend-screen pointer-events-none">
        <source src="/dna-bg.mp4" type="video/mp4" />
      </video>

      {/* =========================================
          VIEW 1: LANDING PAGE
          ========================================= */}
      {appState === 'landing' && (
        <div className="relative z-10 flex flex-col items-center justify-center w-full h-full px-6 text-center backdrop-blur-sm bg-slate-950/40 animate-fade-in">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-8 shadow-[0_0_40px_rgba(59,130,246,0.5)]">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-200 tracking-tight mb-6 drop-shadow-2xl">
            GeneWeave-Risk
          </h1>
          <p className="text-xl md:text-2xl text-blue-100/70 max-w-3xl font-light mb-12 leading-relaxed">
            A dynamic, explainable pharmacogenomic risk engine mapping multi-gene interactions to prevent adverse drug reactions.
          </p>
          <button onClick={() => setAppState('upload')} className="bg-white hover:bg-slate-100 text-slate-900 px-10 py-4 rounded-full font-bold text-lg shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-all transform hover:scale-105 flex items-center">
            Enter Analysis Portal
            <svg className="w-5 h-5 ml-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </div>
      )}

      {/* =========================================
          VIEW 2: ADVANCED VCF UPLOAD STATION
          ========================================= */}
      {appState === 'upload' && (
        <div className="relative z-10 flex flex-col items-center justify-center w-full h-full px-4 md:px-10 backdrop-blur-md bg-slate-950/70 animate-fade-in">
          <div className="w-full max-w-5xl bg-slate-900/80 border border-white/10 rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-2xl flex flex-col md:flex-row">
            
            {/* Left Side Info... */}
            <div className="w-full md:w-5/12 bg-slate-950/50 p-8 md:p-10 border-r border-white/5 flex flex-col justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2 tracking-wide">Data Acquisition</h2>
                <p className="text-sm text-slate-400 mb-8 leading-relaxed">Initialize the GeneWeave interaction pipeline by providing patient variant call data.</p>
              </div>
            </div>

            {/* Right Side Upload Zone */}
            <div className="w-full md:w-7/12 p-8 md:p-12 flex flex-col items-center justify-center relative">
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-600/20 rounded-full blur-[80px] pointer-events-none"></div>

              {/* Hidden File Input wrapped by a Label */}
              <input type="file" id="vcf-upload" accept=".vcf,.gz" className="hidden" onChange={handleFileUpload} />
              
              <label htmlFor="vcf-upload" className="w-full border-2 border-dashed border-blue-500/40 rounded-3xl p-12 bg-gradient-to-b from-blue-900/10 to-transparent hover:border-blue-400 hover:bg-blue-900/20 transition-all cursor-pointer group text-center relative z-10 shadow-inner block">
                <div className="w-20 h-20 bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                  <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Click to Upload VCF File</h3>
                <p className="text-sm text-blue-200/60 mb-6">Executes AI model securely</p>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* =========================================
          VIEW 3: PIPELINE PROCESSING
          ========================================= */}
      {appState === 'processing' && (
        <div className="relative z-10 flex flex-col items-center justify-center w-full h-full px-6 backdrop-blur-xl bg-slate-950/80 animate-fade-in">
          <div className="w-full max-w-lg">
            <h2 className="text-2xl font-bold text-center mb-10 text-blue-400 animate-pulse">Running AI Model...</h2>
            
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-blue-500 before:to-slate-800">
              {loadingMessages.map((msg, index) => (
                <div key={index} className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group transition-all duration-500 ${index <= loadingStep ? 'opacity-100 translate-y-0' : 'opacity-20 translate-y-4'}`}>
                  <div className={`w-10 h-10 rounded-full border-4 shrink-0 flex items-center justify-center shadow-lg z-10 ${index < loadingStep ? 'bg-blue-500 border-blue-400' : index === loadingStep ? 'bg-slate-900 border-blue-400 animate-pulse' : 'bg-slate-900 border-slate-700'}`}>
                    {index < loadingStep && <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>}
                    {index === loadingStep && <div className="w-3 h-3 bg-blue-400 rounded-full"></div>}
                  </div>
                  <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border ${index <= loadingStep ? 'bg-blue-900/20 border-blue-500/30 text-white' : 'bg-slate-900/50 border-white/5 text-slate-500'}`}>
                    <p className="font-bold text-sm">{msg}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =========================================
          VIEW 4: THE DYNAMIC DASHBOARD (Using CatBoost Data)
          ========================================= */}
      {appState === 'dashboard' && analysisResults && (
        <div className="relative z-10 flex flex-col w-full h-full overflow-hidden animate-fade-in">
          
          <header className="h-20 bg-slate-900/50 backdrop-blur-xl border-b border-white/10 flex items-center justify-between px-8 z-20 shrink-0">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white leading-tight">Patient Analysis Complete</h1>
                <p className="text-xs text-slate-400">Processed by CatBoost Hybrid AI Model</p>
              </div>
            </div>
            <button onClick={() => setAppState('upload')} className="bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2 rounded-lg text-sm font-bold flex items-center transition-colors">
              Analyze Another VCF
            </button>
          </header>

          <main className="flex-1 overflow-auto p-6">
            <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
              
              {/* LEFT COLUMN: Extraction & Recommendation */}
              <div className="lg:col-span-4 space-y-6">
                <div className={`${analysisResults.risk_score > 60 ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'} backdrop-blur-xl border rounded-2xl p-6 shadow-lg relative overflow-hidden`}>
                  <h3 className="font-bold uppercase tracking-wider text-xs mb-2 text-white">Final Recommendation</h3>
                  <h2 className="text-3xl font-black text-white mb-1">
                    {analysisResults.risk_score > 60 ? "HIGH RISK DETECTED" : "STANDARD DOSING"}
                  </h2>
                </div>

                <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-lg">
                  <h3 className="text-slate-300 font-bold uppercase tracking-wider text-xs mb-4">AI Feature Input (Genotypes)</h3>
                  <div className="space-y-3">
                    {/* Maps over the new patient_profile object! */}
                    {Object.entries(analysisResults.patient_profile || {}).map(([gene, status], idx) => (
                      <div key={idx} className={`p-3 rounded-lg border flex justify-between ${status === 'Normal' ? 'bg-white/5 border-white/5 text-slate-400' : 'bg-red-500/10 border-red-500/30 text-red-300'}`}>
                        <span className="font-bold">{gene}</span>
                        <span className="font-semibold uppercase text-xs mt-1">{status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* RIGHT COLUMN: Risk Score & Explainability */}
              <div className="lg:col-span-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* The Risk Dial fueled by CatBoost */}
                  <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-lg flex flex-col items-center justify-center relative">
                    <h3 className="absolute top-6 left-6 text-slate-300 font-bold uppercase tracking-wider text-xs">AI Predicted Risk</h3>
                    <div className="relative w-40 h-40 mt-8 mb-4">
                      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1e293b" strokeWidth="8" />
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke={analysisResults.risk_score > 60 ? "#ef4444" : "#10b981"} strokeWidth="8" strokeDasharray="251" strokeDashoffset={251 - (251 * (analysisResults.risk_score / 100))} className="drop-shadow-lg transition-all duration-1000 ease-out" />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-black text-white">{analysisResults.risk_score}<span className="text-xl text-slate-400">%</span></span>
                      </div>
                    </div>
                  </div>

                  {/* Explainability Matrix fueled by CatBoost */}
                  <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-lg">
                    <h3 className="text-slate-300 font-bold uppercase tracking-wider text-xs mb-4">AI Explainability Trace</h3>
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                        <p className="text-sm text-blue-100 font-medium leading-relaxed">
                          {analysisResults.reasoning_trace}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </main>
        </div>
      )}
    </div>
  );
}

export default App;