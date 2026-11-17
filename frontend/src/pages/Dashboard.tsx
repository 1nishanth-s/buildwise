import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  ChevronRight,
  Cpu,
  Folder,
  Plus,
  RefreshCw,
  Sparkles,
  Database,
  TrendingUp,
  Tag,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../services/api';
import { CatalogSummary, Project } from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<CatalogSummary | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [sumRes, projRes] = await Promise.all([
          api.getCatalogSummary(),
          api.getProjects(),
        ]);
        setSummary(sumRes);
        setProjects(projRes);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 grid-bg">
      <div className="max-w-6xl mx-auto space-y-10 animate-fadeIn">
        {/* Hero Section */}
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/15 border border-accent/30 text-accent-soft text-xs font-mono mb-4">
            <Sparkles size={13} className="text-accent-soft" />
            Machine Learning Guided PC Platform
          </div>
          <h1 className="text-4xl font-extrabold text-slate-100 tracking-tight">
            Build your next PC with AI
          </h1>
          <p className="mt-2 text-base text-slate-400 max-w-2xl leading-relaxed">
            Intelligent PC building and upgrade recommendations powered by supervised machine learning
            and deterministic hardware compatibility analysis.
          </p>
        </div>

        {/* Primary Action Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Build Card */}
          <button
            onClick={() => navigate('/build')}
            className="group relative overflow-hidden rounded-2xl border border-canvas-border bg-canvas-panel p-7 text-left hover:border-emerald-500/50 transition-all hover:shadow-2xl hover:shadow-emerald-500/10"
          >
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 opacity-10 blur-3xl group-hover:opacity-20 transition" />
            <div className="relative inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 shadow-lg mb-4">
              <Plus size={24} className="text-white" />
            </div>
            <h3 className="relative text-xl font-bold text-slate-100 mb-2">Build a New PC</h3>
            <p className="relative text-sm text-slate-400 mb-6 leading-relaxed">
              Create an optimized PC configuration from scratch. Provide your primary usage and INR budget;
              our staged engine handles compatibility and ML benchmarks.
            </p>
            <div className="relative inline-flex items-center gap-2 text-sm font-semibold text-emerald-400 group-hover:gap-3 transition-all">
              Start Building <ArrowRight size={16} />
            </div>
          </button>

          {/* Upgrade Card */}
          <button
            onClick={() => navigate('/upgrade')}
            className="group relative overflow-hidden rounded-2xl border border-canvas-border bg-canvas-panel p-7 text-left hover:border-cyan-500/50 transition-all hover:shadow-2xl hover:shadow-cyan-500/10"
          >
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 opacity-10 blur-3xl group-hover:opacity-20 transition" />
            <div className="relative inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 shadow-lg mb-4">
              <RefreshCw size={24} className="text-white" />
            </div>
            <h3 className="relative text-xl font-bold text-slate-100 mb-2">Upgrade Existing PC</h3>
            <p className="relative text-sm text-slate-400 mb-6 leading-relaxed">
              Analyze your current PC setup to identify hardware bottlenecks and discover the best compatible
              component upgrades with estimated ML score deltas.
            </p>
            <div className="relative inline-flex items-center gap-2 text-sm font-semibold text-cyan-400 group-hover:gap-3 transition-all">
              Start Upgrade <ArrowRight size={16} />
            </div>
          </button>
        </div>

        {/* Live Catalog Intelligence Metrics */}
        {summary && (
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-3 flex items-center gap-2">
              <Database size={14} className="text-accent-soft" /> Catalog Intelligence & Model Status
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl border border-canvas-border bg-canvas-panel">
                <div className="text-xs text-slate-400">Total Components</div>
                <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
                  {summary.components_count.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">Verified hardware catalog</div>
              </div>

              <div className="p-4 rounded-xl border border-canvas-border bg-canvas-panel">
                <div className="text-xs text-slate-400">Price Observations</div>
                <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                  {summary.prices_count.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">Indian retail market prices</div>
              </div>

              <div className="p-4 rounded-xl border border-canvas-border bg-canvas-panel">
                <div className="text-xs text-slate-400">CPU ML Model</div>
                <div className="text-base font-bold text-indigo-300 mt-1.5 flex items-center gap-1.5">
                  <CheckCircle2 size={16} className="text-indigo-400" />
                  Cinebench R23
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">Ridge Regression (α=10.0)</div>
              </div>

              <div className="p-4 rounded-xl border border-canvas-border bg-canvas-panel">
                <div className="text-xs text-slate-400">GPU ML Model</div>
                <div className="text-base font-bold text-indigo-300 mt-1.5 flex items-center gap-1.5">
                  <CheckCircle2 size={16} className="text-indigo-400" />
                  Time Spy Graphics
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">Ridge Regression (α=1.0)</div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Projects */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-200 flex items-center gap-2">
              <Folder size={18} className="text-accent-soft" /> Recent Recommendation Projects
            </h2>
          </div>

          {projects.length === 0 ? (
            <div className="p-8 rounded-2xl border border-dashed border-canvas-border text-center text-slate-500">
              No saved recommendations yet. Click "Build a New PC" or "Upgrade Existing PC" to get started!
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.slice(0, 6).map((p) => (
                <button
                  key={p.id}
                  onClick={() => navigate(`/workflow/${p.id}`)}
                  className="text-left p-4 rounded-xl bg-canvas-panel border border-canvas-border hover:border-accent/50 transition group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`text-[10px] uppercase tracking-wider font-mono px-2 py-0.5 rounded-full ${
                        p.mode === 'build'
                          ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                          : 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                      }`}
                    >
                      {p.mode} mode
                    </span>
                    <ChevronRight
                      size={14}
                      className="text-slate-500 group-hover:text-accent-soft group-hover:translate-x-0.5 transition"
                    />
                  </div>
                  <div className="text-sm font-semibold text-slate-100 truncate mb-1" title={p.name}>
                    {p.name}
                  </div>
                  <div className="text-xs text-slate-500 font-mono flex items-center justify-between">
                    <span>{new Date(p.createdAt).toLocaleDateString()}</span>
                    <span className="text-emerald-400 font-semibold">
                      ₹{p.summary?.total ? p.summary.total.toLocaleString() : '0'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
