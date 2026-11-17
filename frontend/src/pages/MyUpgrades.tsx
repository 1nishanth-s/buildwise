import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Folder, RefreshCw, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';

export const MyUpgrades: React.FC = () => {
  const navigate = useNavigate();
  const [upgrades, setUpgrades] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchUpgrades = async () => {
    setLoading(true);
    try {
      const data = await api.getProjects('upgrade');
      setUpgrades(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpgrades();
  }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this upgrade plan?')) return;
    try {
      await api.deleteProject(id);
      setUpgrades(upgrades.filter((u) => u.id !== id));
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-mono mb-2">
              <RefreshCw size={12} /> Saved Plans
            </div>
            <h1 className="text-3xl font-bold text-slate-100">My Upgrade Plans</h1>
            <p className="text-sm text-slate-400 mt-1">
              Review and manage your saved PC upgrade recommendations and performance deltas.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500">Loading saved upgrades...</div>
        ) : upgrades.length === 0 ? (
          <div className="p-12 rounded-2xl border border-dashed border-canvas-border text-center text-slate-500 space-y-3">
            <p>No saved upgrade plans found.</p>
            <button
              onClick={() => navigate('/upgrade')}
              className="px-4 py-2 rounded-xl bg-cyan-600 text-white text-xs font-semibold hover:bg-cyan-500 transition"
            >
              Start An Upgrade Analysis
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {upgrades.map((u) => (
              <div
                key={u.id}
                onClick={() => navigate(`/workflow/${u.id}`)}
                className="group relative p-5 rounded-2xl bg-canvas-panel border border-canvas-border hover:border-cyan-500/50 transition cursor-pointer flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                      Upgrade
                    </span>
                    <button
                      onClick={(e) => handleDelete(e, u.id)}
                      className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-canvas-panelAlt transition"
                      title="Delete upgrade plan"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <h3 className="text-sm font-bold text-slate-100 truncate group-hover:text-cyan-300 transition">
                    {u.name}
                  </h3>
                  <div className="text-xs text-slate-400 mt-1">
                    Goal: {u.inputs?.goal || 'Performance'}
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-canvas-border flex items-center justify-between text-xs font-mono">
                  <span className="text-cyan-400 font-bold text-sm">
                    ₹{u.summary?.total ? u.summary.total.toLocaleString() : '0'} Cost
                  </span>
                  <div className="flex items-center gap-1 text-slate-500 group-hover:text-cyan-300 transition text-[11px] font-sans">
                    View Canvas <ChevronRight size={14} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
