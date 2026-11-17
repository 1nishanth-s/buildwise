import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Folder, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';

export const MyBuilds: React.FC = () => {
  const navigate = useNavigate();
  const [builds, setBuilds] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchBuilds = async () => {
    setLoading(true);
    try {
      const data = await api.getProjects('build');
      setBuilds(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuilds();
  }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this saved build?')) return;
    try {
      await api.deleteProject(id);
      setBuilds(builds.filter((b) => b.id !== id));
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-mono mb-2">
              <Folder size={12} /> Saved Configurations
            </div>
            <h1 className="text-3xl font-bold text-slate-100">My PC Builds</h1>
            <p className="text-sm text-slate-400 mt-1">
              Review and manage your saved PC recommendations. Click any card to reopen the workflow canvas.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500">Loading saved builds...</div>
        ) : builds.length === 0 ? (
          <div className="p-12 rounded-2xl border border-dashed border-canvas-border text-center text-slate-500 space-y-3">
            <p>No saved PC builds found.</p>
            <button
              onClick={() => navigate('/build')}
              className="px-4 py-2 rounded-xl bg-accent text-white text-xs font-semibold hover:bg-accent-dim transition"
            >
              Start Your First PC Build
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {builds.map((b) => (
              <div
                key={b.id}
                onClick={() => navigate(`/workflow/${b.id}`)}
                className="group relative p-5 rounded-2xl bg-canvas-panel border border-canvas-border hover:border-emerald-500/50 transition cursor-pointer flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      {b.inputs?.usage || 'Build'}
                    </span>
                    <button
                      onClick={(e) => handleDelete(e, b.id)}
                      className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-canvas-panelAlt transition"
                      title="Delete build"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <h3 className="text-sm font-bold text-slate-100 truncate group-hover:text-emerald-300 transition">
                    {b.name}
                  </h3>
                  <div className="text-xs text-slate-400 mt-1">
                    {b.componentCount || 8} Recommended Components
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-canvas-border flex items-center justify-between text-xs font-mono">
                  <span className="text-emerald-400 font-bold text-sm">
                    ₹{b.summary?.total ? b.summary.total.toLocaleString() : '0'}
                  </span>
                  <div className="flex items-center gap-1 text-slate-500 group-hover:text-accent-soft transition text-[11px] font-sans">
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
