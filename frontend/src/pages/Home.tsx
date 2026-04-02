import React, { useState, useCallback } from 'react';
import ImageUpload from '../components/ImageUpload';
import AnalysisResults from '../components/AnalysisResults';
import Dashboard from '../components/Dashboard';
import type { AnalysisResult } from '../services/api';
import { analyzeImage } from '../services/api';

type Tab = 'analyze' | 'history';

const Home: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('analyze');
  const [technique, setTechnique] = useState('pixelate');
  const [level, setLevel] = useState('medium');

  const handleFileSelected = useCallback((file: File) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeImage(selectedFile, technique, level);
      setResult(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Analysis failed. Is the backend running?';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 py-4 px-6">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center font-bold text-sm">
            DS
          </div>
          <h1 className="text-xl font-bold tracking-tight">Deepsentrix</h1>
          <span className="text-slate-500 text-sm">AI Deepfake Detection &amp; Protection</span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Tabs */}
        <div className="flex gap-1 bg-slate-800 p-1 rounded-xl w-fit">
          {(['analyze', 'history'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2 rounded-lg text-sm font-medium capitalize transition-colors
                ${activeTab === tab ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'analyze' && (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left column */}
            <div className="space-y-5">
              <h2 className="text-lg font-semibold">Upload Image</h2>
              <ImageUpload onFileSelected={handleFileSelected} disabled={loading} />

              {/* Options */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-xs mb-1 uppercase tracking-wide">
                    Protection technique
                  </label>
                  <select
                    value={technique}
                    onChange={(e) => setTechnique(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="pixelate">Pixelate</option>
                    <option value="blur">Blur</option>
                    <option value="noise">Noise</option>
                    <option value="combined">Combined</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 text-xs mb-1 uppercase tracking-wide">
                    Protection level
                  </label>
                  <select
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
                  rounded-xl py-3 font-semibold transition-colors"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Analysing…
                  </span>
                ) : (
                  'Analyse Image'
                )}
              </button>

              {error && (
                <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300 text-sm">
                  {error}
                </div>
              )}
            </div>

            {/* Right column */}
            <div>
              {result ? (
                <AnalysisResults result={result} />
              ) : (
                <div className="h-full min-h-48 flex items-center justify-center text-slate-600 border-2 border-dashed border-slate-700 rounded-2xl">
                  Results will appear here
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Recent Analyses</h2>
            <Dashboard />
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;
