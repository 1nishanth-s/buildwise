import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Clock, History as HistoryIcon, Workflow } from 'lucide-react';
import { api } from '../services/api';
import { HistoryItem } from '../types';

export const History: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await api.getHistory();
        setHistory(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-accent/10 border border-accent/20 text-accent-soft text-xs font-mono mb-2">
            <HistoryIcon size={12} /> Recommendation Logs
          </div>
          <h1 className="text-3xl font-bold text-slate-100">Generation History</h1>
          <p className="text-sm text-slate-400 mt-1">
            Audit trail of PC build recommendations and upgrade analyses executed by the platform.
          </p>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500">Loading history...</div>
        ) : history.length === 0 ? (
          <div className="p-12 rounded-2xl border border-dashed border-canvas-border text-center text-slate-500">
            No recommendation history recorded yet.
          </div>
        ) : (
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel divide-y divide-canvas-border">
            {history.map((item) => (
              <div
                key={item.id}
                onClick={() => navigate(`/workflow/${item.projectId}`)}
                className="p-4 flex items-center justify-between hover:bg-canvas-panelAlt/50 transition cursor-pointer"
              >
                <div className="flex items-center gap-4 min-w-0">
                  <div
                    className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 ${
                      item.mode === 'build'
                        ? 'bg-emerald-500/15 text-emerald-400'
                        : 'bg-cyan-500/15 text-cyan-400'
                    }`}
                  >
                    <Workflow size={20} />
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[9px] uppercase font-mono px-1.5 py-0.2 rounded font-bold ${
                          item.mode === 'build'
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : 'bg-cyan-500/20 text-cyan-300'
                        }`}
                      >
                        {item.mode}
                      </span>
                      <span className="text-xs font-bold text-slate-200 truncate">
                        {item.mode === 'build'
                          ? `${item.inputs?.usage || 'Build'} · ₹${item.inputs?.budget?.toLocaleString()}`
                          : `Upgrade · ${item.inputs?.goal || 'Performance'}`}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                      <Clock size={11} />
                      {new Date(item.createdAt).toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right">
                    <div className="text-xs font-bold font-mono text-emerald-400">
                      ₹{item.summary?.total ? item.summary.total.toLocaleString() : '0'}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      Target ₹{item.summary?.budget ? item.summary.budget.toLocaleString() : '0'}
                    </div>
                  </div>

                  <ChevronRight size={16} className="text-slate-500" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
