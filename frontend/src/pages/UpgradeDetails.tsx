import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  Box,
  Cpu,
  HardDrive,
  MemoryStick,
  Monitor,
  Package,
  RefreshCw,
  Sparkles,
  Zap,
  Fan,
  AlertCircle,
  Gamepad2,
  Film,
  Code2,
} from 'lucide-react';
import { api } from '../services/api';

export const UpgradeDetails: React.FC = () => {
  const navigate = useNavigate();

  const [existing, setExisting] = useState<Record<string, string>>({
    cpu: 'Ryzen 5 3600',
    gpu: 'GTX 1660 Super',
    motherboard: 'B450',
    ram: '16GB',
    storage: '500GB SSD',
    psu: '550W',
    cooler: '',
    caseName: '',
  });

  const [budget, setBudget] = useState<string>('35000');
  const [goal, setGoal] = useState<string>('Better Gaming Performance');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const budgetNum = parseInt(budget.replace(/[^0-9]/g, ''), 10) || 0;
  const canSubmit = budgetNum >= 5000 && Boolean(goal) && !loading;

  const goalOptions = [
    { id: 'Better Gaming Performance', label: 'Better Gaming Performance', icon: Gamepad2, desc: 'Upgrade GPU and graphic rendering power.' },
    { id: 'Higher FPS', label: 'Higher FPS in Esports Titles', icon: Sparkles, desc: 'High-refresh competitive gaming speed.' },
    { id: 'Faster Video Editing', label: 'Faster Video Editing & Rendering', icon: Film, desc: 'Boost timeline playback and encoding speed.' },
    { id: 'Faster Productivity / Dev', label: 'Faster Programming & Compiling', icon: Code2, desc: 'Upgrade multi-core CPU capacity and RAM.' },
    { id: 'More Storage', label: 'More Storage Capacity', icon: HardDrive, desc: 'Add fast high-capacity NVMe SSD.' },
    { id: 'Balanced Overall Upgrade', label: 'Balanced Overall Upgrade', icon: RefreshCw, desc: 'Well-rounded upgrade across bottlenecked parts.' },
  ];

  const hardwareFields = [
    { key: 'cpu', label: 'Processor (CPU)', icon: Cpu, placeholder: 'e.g. AMD Ryzen 5 3600 or Intel Core i5-10400' },
    { key: 'gpu', label: 'Graphics Card (GPU)', icon: Monitor, placeholder: 'e.g. NVIDIA GTX 1660 Super or RTX 2060' },
    { key: 'motherboard', label: 'Motherboard', icon: Package, placeholder: 'e.g. MSI B450 TOMAHAWK or ASUS B550' },
    { key: 'ram', label: 'RAM Memory', icon: MemoryStick, placeholder: 'e.g. 16GB DDR4 3200MHz' },
    { key: 'storage', label: 'Current Storage', icon: HardDrive, placeholder: 'e.g. 500GB Kingston NVMe SSD' },
    { key: 'psu', label: 'Power Supply Unit (PSU)', icon: Zap, placeholder: 'e.g. Corsair CV550 550W 80+' },
    { key: 'cooler', label: 'CPU Cooler (Optional)', icon: Fan, placeholder: 'e.g. Stock AMD Wraith Stealth', optional: true },
    { key: 'caseName', label: 'PC Case (Optional)', icon: Box, placeholder: 'e.g. Cooler Master Q300L', optional: true },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    setError(null);

    try {
      const project = await api.recommendUpgrade({
        existing,
        budget: budgetNum,
        goal,
      });
      navigate(`/workflow/${project.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze PC and recommend upgrades.');
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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-3">
            <RefreshCw size={13} /> Upgrade Mode
          </div>
          <h1 className="text-3xl font-bold text-slate-100">Upgrade your existing PC</h1>
          <p className="mt-1 text-sm text-slate-400">
            Tell us about your current configuration and upgrade budget. We'll identify system
            bottlenecks, preserve reusable hardware, and recommend compatible upgrades.
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-xl border border-red-500/30 bg-red-950/30 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section A: Existing Hardware */}
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div>
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Box size={16} className="text-cyan-400" /> Current PC Hardware Configuration
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Enter your existing components. We'll verify socket compatibility and PSU capacity.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 gap-3">
              {hardwareFields.map((field) => {
                const Icon = field.icon;
                return (
                  <div key={field.key} className="space-y-1">
                    <label className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                      <Icon size={12} className="text-slate-500" />
                      {field.label}
                      {field.optional && <span className="text-slate-600 font-normal">(optional)</span>}
                    </label>
                    <input
                      type="text"
                      value={existing[field.key] || ''}
                      onChange={(e) =>
                        setExisting({ ...existing, [field.key]: e.target.value })
                      }
                      placeholder={field.placeholder}
                      className="w-full px-3 py-2 rounded-xl bg-canvas-panelAlt border border-canvas-border focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 text-xs text-slate-200 placeholder-slate-600"
                    />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section B: Upgrade Goal */}
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div>
              <label className="text-sm font-bold text-slate-200">Upgrade Goal</label>
              <p className="text-xs text-slate-400 mt-0.5">
                What is your main priority for this upgrade?
              </p>
            </div>

            <div className="grid sm:grid-cols-2 gap-2.5">
              {goalOptions.map((opt) => {
                const Icon = opt.icon;
                const isSelected = goal === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setGoal(opt.id)}
                    className={`p-3 rounded-xl border text-left transition flex items-start gap-3 ${
                      isSelected
                        ? 'border-cyan-500 bg-cyan-950/30 ring-1 ring-cyan-500 shadow-lg shadow-cyan-500/10'
                        : 'border-canvas-border bg-canvas-panelAlt hover:border-canvas-borderAlt'
                    }`}
                  >
                    <div
                      className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected ? 'bg-cyan-500 text-slate-900' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      <Icon size={16} />
                    </div>
                    <div className="min-w-0">
                      <div
                        className={`text-xs font-bold ${
                          isSelected ? 'text-slate-100' : 'text-slate-300'
                        }`}
                      >
                        {opt.label}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5">{opt.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section C: Upgrade Budget */}
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div>
              <label htmlFor="upgrade-budget" className="text-sm font-bold text-slate-200">
                Upgrade Budget (INR)
              </label>
              <p className="text-xs text-slate-400 mt-0.5">
                Maximum funds to allocate strictly for new replacement components.
              </p>
            </div>

            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg font-bold font-mono text-slate-400">
                ₹
              </span>
              <input
                id="upgrade-budget"
                type="text"
                value={budget}
                onChange={(e) => {
                  const cleaned = e.target.value.replace(/[^0-9]/g, '');
                  setBudget(cleaned);
                }}
                placeholder="35,000"
                className="w-full pl-9 pr-4 py-3 rounded-xl bg-canvas-panelAlt border border-canvas-border focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 text-base font-bold font-mono text-slate-100"
              />
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              {[20000, 35000, 50000, 75000, 100000].map((preset) => (
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
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={!canSubmit}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-xl shadow-cyan-500/20 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Sparkles size={18} className="animate-spin" />
                Analyzing Bottlenecks & Recommending Upgrades...
              </>
            ) : (
              <>
                Analyze My PC and Recommend Upgrades <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
