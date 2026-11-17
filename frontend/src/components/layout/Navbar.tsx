import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Sparkles, Workflow } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="h-14 border-b border-canvas-border bg-canvas-panel/90 backdrop-blur-md px-6 flex items-center justify-between z-20">
      <div className="flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Cpu size={18} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight text-slate-100 flex items-center gap-1.5">
              BuildWise-AI
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                v2.0
              </span>
            </div>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-[11px] text-indigo-300 font-mono">
          <Sparkles size={12} className="text-indigo-400 animate-pulse" />
          <span>Ridge Regression Models Active</span>
        </div>

        <Link
          to="/history"
          className="p-1.5 rounded-lg border border-canvas-border text-slate-400 hover:text-slate-200 hover:bg-canvas-panelAlt transition"
          title="Recommendation History"
        >
          <Workflow size={16} />
        </Link>
      </div>
    </header>
  );
};
