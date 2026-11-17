import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  RefreshCw,
  Folder,
  History,
  Settings,
  Sparkles,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/build', label: 'Build a PC', icon: Cpu },
    { to: '/upgrade', label: 'Upgrade a PC', icon: RefreshCw },
    { to: '/my-builds', label: 'My Builds', icon: Folder },
    { to: '/my-upgrades', label: 'My Upgrades', icon: Folder },
    { to: '/history', label: 'History', icon: History },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-56 shrink-0 border-r border-canvas-border bg-canvas-panel flex flex-col justify-between p-3 select-none">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-slate-500">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition ${
                  isActive
                    ? 'bg-accent/15 text-accent-soft font-semibold border border-accent/30 shadow-sm shadow-accent/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-canvas-panelAlt'
                }`
              }
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt p-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-200 mb-1">
          <Sparkles size={13} className="text-accent-soft" />
          <span>ML Inference</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-snug">
          Predictions strictly isolated to CPU Multi-Core & GPU Graphics pipelines.
        </p>
      </div>
    </aside>
  );
};
