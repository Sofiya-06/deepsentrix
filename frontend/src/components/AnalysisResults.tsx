import React from 'react';
import type { AnalysisResult } from '../services/api';

interface Props {
  result: AnalysisResult;
}

const ConfidenceBar: React.FC<{ value: number; isFake: boolean }> = ({ value, isFake }) => (
  <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
    <div
      className={`h-3 rounded-full transition-all duration-700 ${isFake ? 'bg-red-500' : 'bg-emerald-500'}`}
      style={{ width: `${Math.round(value * 100)}%` }}
    />
  </div>
);

const AnalysisResults: React.FC<Props> = ({ result }) => {
  const confidencePct = Math.round(result.confidence * 100);
  const isFake = result.is_fake;

  return (
    <div className="bg-slate-800 rounded-2xl p-6 space-y-5 text-white">
      {/* Header badge */}
      <div className="flex items-center gap-3">
        <span
          className={`px-4 py-1 rounded-full text-sm font-bold uppercase tracking-wider
            ${isFake ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'}`}
        >
          {isFake ? '⚠ Deepfake Detected' : '✓ Authentic Image'}
        </span>
      </div>

      {/* Confidence */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-slate-400">Confidence</span>
          <span className={`font-semibold ${isFake ? 'text-red-400' : 'text-emerald-400'}`}>
            {confidencePct}%
          </span>
        </div>
        <ConfidenceBar value={result.confidence} isFake={isFake} />
      </div>

      {/* Metadata grid */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-slate-400 text-xs uppercase tracking-wide">File</p>
          <p className="font-medium truncate">{result.filename}</p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-slate-400 text-xs uppercase tracking-wide">Type</p>
          <p className="font-medium capitalize">{result.detection_type}</p>
        </div>
        {result.protection_technique && (
          <div className="bg-slate-700/50 rounded-lg p-3">
            <p className="text-slate-400 text-xs uppercase tracking-wide">Protection</p>
            <p className="font-medium capitalize">{result.protection_technique}</p>
          </div>
        )}
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-slate-400 text-xs uppercase tracking-wide">Result ID</p>
          <p className="font-mono text-xs truncate">{result.result_id.split('-')[0]}</p>
        </div>
      </div>

      {/* Details */}
      <details className="group">
        <summary className="cursor-pointer text-slate-400 text-sm hover:text-slate-200 transition-colors">
          Technical details ▸
        </summary>
        <pre className="mt-2 bg-slate-900 rounded-lg p-3 text-xs text-slate-300 overflow-x-auto">
          {JSON.stringify(result.details, null, 2)}
        </pre>
      </details>

      {/* Protected image */}
      {result.protected_image && (
        <div>
          <p className="text-slate-400 text-sm mb-2">Protected image</p>
          <img
            src={`data:image/jpeg;base64,${result.protected_image}`}
            alt="Protected"
            className="rounded-xl w-full max-h-64 object-contain bg-slate-900"
          />
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
