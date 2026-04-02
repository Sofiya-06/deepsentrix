import React, { useEffect, useState } from 'react';
import type { StoredResult } from '../services/api';
import { listResults } from '../services/api';

const Dashboard: React.FC = () => {
  const [results, setResults] = useState<StoredResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listResults(10)
      .then(setResults)
      .catch(() => setError('Could not load recent results.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="text-center py-10 text-slate-400 animate-pulse">Loading history…</div>
    );
  }

  if (error) {
    return <p className="text-red-400 text-sm text-center py-6">{error}</p>;
  }

  if (results.length === 0) {
    return (
      <p className="text-slate-500 text-sm text-center py-6">
        No analyses yet. Upload an image above to get started.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-700 text-slate-300 uppercase text-xs tracking-wide">
          <tr>
            <th className="px-4 py-3">File</th>
            <th className="px-4 py-3">Result</th>
            <th className="px-4 py-3">Confidence</th>
            <th className="px-4 py-3">Date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {results.map((r) => (
            <tr key={r.result_id} className="hover:bg-slate-700/40 transition-colors">
              <td className="px-4 py-3 font-medium truncate max-w-xs">{r.filename}</td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                    r.is_fake
                      ? 'bg-red-500/20 text-red-400'
                      : 'bg-emerald-500/20 text-emerald-400'
                  }`}
                >
                  {r.is_fake ? 'Fake' : 'Real'}
                </span>
              </td>
              <td className="px-4 py-3">{Math.round(r.confidence * 100)}%</td>
              <td className="px-4 py-3 text-slate-400">
                {new Date(r.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
