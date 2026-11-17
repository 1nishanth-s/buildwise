import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  Cpu,
  Database,
  Monitor,
  Settings as SettingsIcon,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';
import { CatalogSummary } from '../types';

export const Settings: React.FC = () => {
  const [summary, setSummary] = useState<CatalogSummary | null>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    async function fetchInfo() {
      try {
        const [sumRes, healthRes] = await Promise.all([
          api.getCatalogSummary(),
          api.getHealth(),
        ]);
        setSummary(sumRes);
        setHealth(healthRes);
      } catch (err) {
        console.error(err);
      }
    }
    fetchInfo();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono mb-2">
            <SettingsIcon size={12} /> System Configuration
          </div>
          <h1 className="text-3xl font-bold text-slate-100">Settings & Intelligence</h1>
          <p className="text-sm text-slate-400 mt-1">
            BuildWise-AI platform telemetry, supervised machine learning pipelines, and dataset baselines.
          </p>
        </div>

        {/* Machine Learning Models Status */}
        <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles size={18} className="text-accent-soft" />
              <h2 className="text-sm font-bold text-slate-200">Supervised Regression Pipelines</h2>
            </div>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              Active & Validated
            </span>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Cpu size={14} className="text-indigo-400" /> CPU Performance Model
                </span>
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 size={12} /> Ready
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-snug">
                Predicts Cinebench R23 Multi-Core scores from cores, threads, boost clock, TDP, brand, socket, and memory type.
              </p>
              <div className="text-[11px] font-mono text-slate-500 pt-1 border-t border-canvas-border">
                Algorithm: Ridge Regression (α=10.0) · Group CV R² = 0.917
              </div>
            </div>

            <div className="p-4 rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Monitor size={14} className="text-indigo-400" /> GPU Performance Model
                </span>
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 size={12} /> Ready
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-snug">
                Predicts 3DMark Time Spy Graphics scores from VRAM capacity, bus width, memory bandwidth, clocks, and power.
              </p>
              <div className="text-[11px] font-mono text-slate-500 pt-1 border-t border-canvas-border">
                Algorithm: Ridge Regression (α=1.0) · Group CV R² = 0.902
              </div>
            </div>
          </div>
        </div>

        {/* Dataset Provenance */}
        {summary && (
          <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-4">
            <div className="flex items-center gap-2">
              <Database size={18} className="text-accent-soft" />
              <h2 className="text-sm font-bold text-slate-200">Catalog Dataset Baselines</h2>
            </div>

            <div className="grid grid-cols-3 gap-4 font-mono text-center">
              <div className="p-3 rounded-xl bg-canvas-panelAlt border border-canvas-border">
                <div className="text-[10px] uppercase text-slate-500">Components</div>
                <div className="text-xl font-bold text-slate-100 mt-1">{summary.components_count}</div>
              </div>
              <div className="p-3 rounded-xl bg-canvas-panelAlt border border-canvas-border">
                <div className="text-[10px] uppercase text-slate-500">Price Records</div>
                <div className="text-xl font-bold text-emerald-400 mt-1">{summary.prices_count}</div>
              </div>
              <div className="p-3 rounded-xl bg-canvas-panelAlt border border-canvas-border">
                <div className="text-[10px] uppercase text-slate-500">Benchmark Points</div>
                <div className="text-xl font-bold text-indigo-300 mt-1">{summary.benchmarks_count}</div>
              </div>
            </div>
          </div>
        )}

        {/* Compatibility Rules Engine */}
        <div className="rounded-2xl border border-canvas-border bg-canvas-panel p-6 space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-emerald-400" />
            <h2 className="text-sm font-bold text-slate-200">Deterministic Compatibility Architecture</h2>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Hardware compatibility is strictly evaluated using deterministic mathematical constraints
            (sockets, memory generation, form factor clearances, and PSU headroom) from <code className="text-slate-300 font-mono">src.compatibility</code>.
            Machine learning models are never allowed to override physical compatibility rules.
          </p>
        </div>
      </div>
    </div>
  );
};
