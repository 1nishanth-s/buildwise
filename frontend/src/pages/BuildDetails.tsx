import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Code2,
  Gamepad2,
  LayoutDashboard,
  Plus,
  Sparkles,
  Video,
  BoxSelect,
  AlertCircle,
} from 'lucide-react';
import { api } from '../services/api';

export const BuildDetails: React.FC = () => {
  const navigate = useNavigate();

  // Exactly TWO inputs
  const [usage, setUsage] = useState<string>('Gaming');
  const [budget, setBudget] = useState<string>('75000');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const budgetNum = parseInt(budget.replace(/[^0-9]/g, ''), 10) || 0;
  const isValidBudget = budgetNum >= 18000;
  const canSubmit = Boolean(usage) && isValidBudget && !loading;

  const usageOptions = [
    {
      id: 'Gaming',
      label: 'Gaming',
      icon: Gamepad2,
      desc: 'High frame rates, ultra settings, and ray tracing in modern AAA titles.',
    },
    {
      id: 'Content Creation',
      label: 'Content Creation / Video Editing',
      icon: Video,
      desc: '4K/8K timeline playback, multi-track timeline editing, and accelerated rendering.',
    },
    {
      id: 'Productivity / Workstation',
      label: 'Productivity / Workstation',
      icon: Code2,
      desc: 'Fast code compilation, multi-core capacity for VMs, docker, and massive multitasking.',
    },
    {
      id: '3D Rendering',
      label: '3D Rendering & Animation',
      icon: BoxSelect,
      desc: 'Blender, Maya, Cinema4D rendering with maximum GPU compute power.',
    },
    {
      id: 'Office / Study',
      label: 'Office / Study',
      icon: Briefcase,
      desc: 'Snappy everyday productivity, research, browsing, and quiet energy efficiency.',
    },
    {
      id: 'General Purpose',
      label: 'General Purpose',
      icon: LayoutDashboard,
      desc: 'Balanced all-round home desktop for multimedia, browsing, and casual tasks.',
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    setError(null);

    try {
      const project = await api.recommendBuild({
        usage,
        budget: budgetNum,
      });
      navigate(`/workflow/${project.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to generate build recommendation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition"
        >
          <ArrowLeft size={14} /> Back to Dashboard
        </button>

        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono mb-3">
            <Plus size={13} /> Build Mode
          </div>
          <h1 className="text-3xl font-bold text-slate-100">Configure your new PC</h1>
          <p className="mt-1 text-sm text-slate-400">
            Provide your primary intended use case and budget in Indian Rupees. BuildWise-AI will
            deterministically select compatible hardware, verify prices, and predict ML performance.
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-xl border border-red-500/30 bg-red-950/30 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Input 1: Primary Usage */}
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-bold text-slate-200">1. Primary Usage</label>
                <p className="text-xs text-slate-400 mt-0.5">
                  Select how you plan to use this computer. Component budget weighting adapts accordingly.
                </p>
              </div>
              <span className="text-xs font-mono font-semibold text-accent-soft">
                {usage}
              </span>
            </div>

            <div className="grid sm:grid-cols-2 gap-3">
              {usageOptions.map((opt) => {
                const Icon = opt.icon;
                const isSelected = usage === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setUsage(opt.id)}
                    className={`p-4 rounded-xl border text-left transition relative flex flex-col justify-between ${
                      isSelected
                        ? 'border-accent bg-accent/15 shadow-lg shadow-accent/10 ring-1 ring-accent'
                        : 'border-canvas-border bg-canvas-panelAlt hover:border-canvas-borderAlt'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div
                          className={`h-9 w-9 rounded-lg flex items-center justify-center ${
                            isSelected ? 'bg-accent text-white' : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          <Icon size={18} />
                        </div>
                        {isSelected && (
                          <CheckCircle2 size={18} className="text-accent-soft" />
                        )}
                      </div>
                      <div
                        className={`text-sm font-bold ${
                          isSelected ? 'text-slate-100' : 'text-slate-300'
                        }`}
                      >
                        {opt.label}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                        {opt.desc}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Input 2: Total Budget */}
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div>
              <label htmlFor="budget-input" className="text-sm font-bold text-slate-200">
                2. Total Budget (INR)
              </label>
              <p className="text-xs text-slate-400 mt-0.5">
                Target budget in Indian Rupees (₹). Includes all essential components.
              </p>
            </div>

            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg font-bold font-mono text-slate-400">
                ₹
              </span>
              <input
                id="budget-input"
                type="text"
                value={budget}
                onChange={(e) => {
                  const cleaned = e.target.value.replace(/[^0-9]/g, '');
                  setBudget(cleaned);
                }}
                placeholder="75,000"
                className="w-full pl-9 pr-4 py-3 rounded-xl bg-canvas-panelAlt border border-canvas-border focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 text-base font-bold font-mono text-slate-100"
              />
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              {[45000, 65000, 85000, 120000, 160000, 220000].map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => setBudget(preset.toString())}
                  className="px-2.5 py-1 rounded-lg bg-canvas-panelAlt border border-canvas-border hover:border-canvas-borderAlt text-[11px] font-mono text-slate-400 hover:text-slate-200 transition"
                >
                  ₹{preset.toLocaleString()}
                </button>
              ))}
            </div>

            {!isValidBudget && budgetNum > 0 && (
              <p className="text-xs text-amber-400 flex items-center gap-1.5">
                <AlertCircle size={13} /> Minimum viable budget for a complete PC with catalog components is ₹18,000.
              </p>
            )}
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={!canSubmit}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold text-sm shadow-xl shadow-emerald-500/20 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Sparkles size={18} className="animate-spin" />
                Generating Recommendations & ML Predictions...
              </>
            ) : (
              <>
                Generate My PC Build <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
