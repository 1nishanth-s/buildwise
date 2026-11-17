import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import {
  Brain,
  CheckCircle2,
  Circle,
  Cpu,
  Fan,
  HardDrive,
  LayoutDashboard,
  MemoryStick,
  Monitor,
  Package,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  Wallet,
  Zap,
} from 'lucide-react';
import { WorkflowNodeData } from '../../types';

export type WorkflowNodeType = Node<WorkflowNodeData, 'workflowNode'>;

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  cpu: Cpu,
  gpu: Monitor,
  motherboard: LayoutDashboard,
  ram: MemoryStick,
  storage: HardDrive,
  psu: Zap,
  case: Package,
  cooler: Fan,
};

const KIND_ICONS: Record<string, React.ElementType> = {
  requirements: Sparkles,
  budget: Wallet,
  ai: Brain,
  compat: ShieldCheck,
  analysis: Brain,
  final: CheckCircle2,
  existing: Package,
};

export const WorkflowNode: React.FC<NodeProps<WorkflowNodeType>> = memo(({ data, selected }) => {
  const kind = data.kind || 'component';
  const cat = data.category || '';
  const status = data.status || 'pending';

  const IconComponent =
    kind === 'component'
      ? CATEGORY_ICONS[cat] || Circle
      : KIND_ICONS[kind] || Circle;

  // Visual status border & background styles
  const statusBorderStyles: Record<string, string> = {
    pending: 'border-canvas-borderAlt bg-canvas-panel',
    recommended: 'border-indigo-500/60 bg-gradient-to-br from-canvas-panel to-indigo-950/40',
    selected: 'border-accent bg-gradient-to-br from-canvas-panel to-indigo-950/60',
    compatible: 'border-status-ok/60 bg-gradient-to-br from-canvas-panel to-emerald-950/30',
    incompatible: 'border-status-err/60 bg-gradient-to-br from-canvas-panel to-red-950/30',
    existing: 'border-cyan-500/50 bg-gradient-to-br from-canvas-panel to-cyan-950/30',
    reusable: 'border-slate-500/50 bg-gradient-to-br from-canvas-panel to-slate-900/40',
    warning: 'border-status-warn/60 bg-gradient-to-br from-canvas-panel to-amber-950/30',
    dependency: 'border-amber-500/60 bg-gradient-to-br from-canvas-panel to-amber-950/40',
  };

  const statusPills: Record<string, { text: string; color: string }> = {
    pending: { text: 'Pending', color: 'text-slate-400' },
    recommended: { text: 'Recommended', color: 'text-indigo-300' },
    selected: { text: 'Active', color: 'text-indigo-200' },
    compatible: { text: 'Compatible', color: 'text-emerald-300' },
    incompatible: { text: 'Incompatible', color: 'text-red-300' },
    existing: { text: 'Installed', color: 'text-cyan-300' },
    reusable: { text: 'Retained', color: 'text-slate-300' },
    warning: { text: 'Notice', color: 'text-amber-300' },
    dependency: { text: 'Required Dependency', color: 'text-amber-300' },
  };

  const iconColors: Record<string, string> = {
    component: 'bg-indigo-500/15 text-indigo-400',
    requirements: 'bg-cyan-500/15 text-cyan-400',
    budget: 'bg-amber-500/15 text-amber-400',
    ai: 'bg-fuchsia-500/15 text-fuchsia-400',
    compat: status === 'incompatible' ? 'bg-red-500/15 text-red-400' : 'bg-emerald-500/15 text-emerald-400',
    analysis: 'bg-purple-500/15 text-purple-400',
    final: 'bg-emerald-500/15 text-emerald-400',
    existing: 'bg-cyan-500/15 text-cyan-400',
  };

  // Compatibility badge resolution for component nodes
  const compatBadge = (() => {
    if (kind !== 'component') return null;
    if (data.compatStatus === 'incompatible' || status === 'incompatible') {
      return {
        label: 'Incompatible',
        className: 'bg-red-500/15 text-red-300 border border-red-500/30',
      };
    }
    if (data.compatStatus === 'warning' || status === 'warning') {
      return {
        label: 'Review Needed',
        className: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
      };
    }
    return {
      label: 'Compatible',
      className: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30',
    };
  })();

  return (
    <div
      className={`relative w-[290px] rounded-2xl border ${
        statusBorderStyles[status] || statusBorderStyles.pending
      } shadow-xl backdrop-blur-md transition-all hover:scale-[1.02] cursor-pointer ${
        selected ? 'ring-2 ring-accent shadow-indigo-500/30' : ''
      }`}
    >
      {/* Target Handles */}
      <Handle
        type="target"
        position={Position.Left}
        id="target-left"
        style={{
          top: '50%',
          background: '#1e293b',
          borderColor: '#64748b',
          borderWidth: 2,
          width: 9,
          height: 9,
        }}
      />
      <Handle
        type="target"
        position={Position.Top}
        id="target-top"
        style={{
          left: '50%',
          background: '#1e293b',
          borderColor: '#64748b',
          borderWidth: 2,
          width: 9,
          height: 9,
        }}
      />

      <div className="p-3.5">
        <div className="flex items-start gap-3">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-inner ${
              iconColors[kind] || 'bg-slate-800 text-slate-300'
            }`}
          >
            <IconComponent size={20} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold truncate">
                {kind === 'component' ? cat : kind}
              </span>
              <div className="flex items-center gap-1.5 shrink-0">
                {compatBadge && (
                  <span className={`text-[9px] font-semibold px-1.5 py-0.2 rounded ${compatBadge.className}`}>
                    {compatBadge.label}
                  </span>
                )}
                <span className={`text-[10px] font-medium flex items-center gap-1 ${statusPills[status]?.color || 'text-slate-400'}`}>
                  ● {statusPills[status]?.text || status}
                </span>
              </div>
            </div>

            <div className="mt-1 text-xs font-bold text-slate-100 truncate" title={data.label}>
              {data.label}
            </div>

            {data.subtitle && (
              <div className="text-[11px] text-slate-400 truncate">{data.subtitle}</div>
            )}

            {/* Component Upgrade Role Pill */}
            {data.upgrade_role && (
              <div className="mt-1 flex items-center gap-1">
                <span
                  className={`text-[9px] font-semibold px-1.5 py-0.2 rounded border ${
                    data.upgrade_role === 'primary'
                      ? 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
                      : data.upgrade_role === 'dependency'
                      ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                      : data.upgrade_role === 'unresolved'
                      ? 'bg-red-500/15 text-red-300 border-red-500/30'
                      : 'bg-slate-700/30 text-slate-400 border-slate-600/30'
                  }`}
                >
                  {data.upgrade_role === 'primary'
                    ? 'Primary Upgrade'
                    : data.upgrade_role === 'dependency'
                    ? 'Required Dependency'
                    : data.upgrade_role === 'unresolved'
                    ? 'Unresolved'
                    : 'Retained'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Non-component brief description only (Requirements, Final, Existing) */}
        {kind !== 'component' && data.description && (
          <div className="mt-2 text-[11px] text-slate-400 leading-snug line-clamp-2">
            {data.description}
          </div>
        )}

        {/* Specs highlights */}
        {data.specs && Object.keys(data.specs).length > 0 && (
          <div className="mt-2.5 grid grid-cols-2 gap-x-2 gap-y-1 bg-canvas-panelAlt/80 rounded-lg p-2 border border-canvas-border/60">
            {Object.entries(data.specs)
              .slice(0, 4)
              .map(([key, val]) => (
                <div key={key} className="text-[10px] flex items-center justify-between">
                  <span className="text-slate-500 truncate capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-slate-300 font-mono font-medium truncate ml-1">
                    {String(val)}
                  </span>
                </div>
              ))}
          </div>
        )}

        {/* ML Performance Estimate Badge for CPU or GPU */}
        {data.mlPrediction && data.mlPrediction.status === 'success' && data.mlPrediction.score && (
          <div className="mt-2.5 flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-indigo-950/70 border border-indigo-500/30 text-[10px]">
            <span className="text-indigo-300 flex items-center gap-1 font-medium">
              <Sparkles size={11} className="text-indigo-400" />
              {cat === 'cpu' ? 'Cinebench R23' : cat === 'gpu' ? 'Time Spy Graphics' : 'ML Estimate'}
            </span>
            <span className="font-mono font-bold text-indigo-200">
              {Math.round(data.mlPrediction.score).toLocaleString()} pts
            </span>
          </div>
        )}

        {/* Formatted INR Price Row */}
        {typeof data.price === 'number' && (
          <div className="mt-2.5 pt-2 border-t border-canvas-border flex items-center justify-between">
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400">
              {status === 'reusable' || data.upgrade_role === 'retained' ? 'Retained Cost' : 'Price'}
            </span>
            <span className="text-xs font-bold font-mono text-emerald-400">
              {status === 'reusable' || data.upgrade_role === 'retained' ? '₹0 (Kept)' : `₹${data.price.toLocaleString()}`}
            </span>
          </div>
        )}
      </div>

      {/* Source Handles */}
      <Handle
        type="source"
        position={Position.Right}
        id="source-right"
        style={{
          top: '50%',
          background: '#1e293b',
          borderColor: '#64748b',
          borderWidth: 2,
          width: 9,
          height: 9,
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="source-bottom"
        style={{
          left: '50%',
          background: '#1e293b',
          borderColor: '#64748b',
          borderWidth: 2,
          width: 9,
          height: 9,
        }}
      />
    </div>
  );
});
