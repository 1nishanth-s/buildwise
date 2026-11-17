import React, { useState } from 'react';
import {
  Brain,
  CheckCircle2,
  ExternalLink,
  Info,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Store,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { WorkflowNodeData } from '../../types';

interface PropertiesPanelProps {
  nodeData: WorkflowNodeData | null;
  onClose: () => void;
  onReplaceComponent: (category: string, newComponentId: string) => Promise<void>;
  isReplacing?: boolean;
}

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  nodeData,
  onClose,
  onReplaceComponent,
  isReplacing = false,
}) => {
  const [showAlternatives, setShowAlternatives] = useState(false);

  if (!nodeData) {
    return (
      <div className="w-80 border-l border-canvas-border bg-canvas-panel p-6 flex flex-col items-center justify-center text-center text-slate-500 select-none">
        <Info size={32} className="text-slate-600 mb-3" />
        <p className="text-xs font-medium">Select any node on the canvas to inspect hardware specifications and alternatives.</p>
      </div>
    );
  }

  const isComponent = nodeData.kind === 'component' || nodeData.kind === 'existing';

  return (
    <aside className="w-84 md:w-96 border-l border-canvas-border bg-canvas-panel flex flex-col h-full overflow-hidden select-none z-10 animate-fadeIn">
      {/* Header */}
      <div className="p-4 border-b border-canvas-border flex items-center justify-between bg-canvas-panelAlt/50">
        <div className="min-w-0">
          <span className="text-[10px] uppercase font-mono tracking-wider text-accent-soft font-semibold">
            {isComponent ? `${nodeData.category} details` : `${nodeData.kind} analysis`}
          </span>
          <h2 className="text-sm font-bold text-slate-100 truncate" title={nodeData.label}>
            {nodeData.label}
          </h2>
          {nodeData.subtitle && (
            <div className="text-xs text-slate-400 truncate">{nodeData.subtitle}</div>
          )}
          {nodeData.upgrade_role && (
            <div className="mt-1 flex items-center gap-1.5">
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                nodeData.upgrade_role === 'primary'
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                  : nodeData.upgrade_role === 'dependency'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : nodeData.upgrade_role === 'retained'
                  ? 'bg-slate-700/40 text-slate-300 border-slate-600/40'
                  : 'bg-red-500/20 text-red-300 border-red-500/40'
              }`}>
                {nodeData.upgrade_role === 'primary' ? 'Primary Upgrade'
                  : nodeData.upgrade_role === 'dependency' ? 'Required Dependency'
                  : nodeData.upgrade_role === 'retained' ? 'Retained Component'
                  : 'Unresolved Incompatibility'}
              </span>
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-canvas-border transition"
        >
          <X size={16} />
        </button>
      </div>

      {/* Body scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Required Dependency Reason */}
        {nodeData.dependency_reason && (
          <div className="rounded-xl border border-amber-500/40 bg-gradient-to-br from-canvas-panelAlt to-amber-950/30 p-3.5 space-y-1.5">
            <div className="text-[10px] uppercase font-mono tracking-wider text-amber-300 font-semibold flex items-center gap-1.5">
              <ShieldAlert size={12} className="text-amber-400" /> Required Dependency Reason
            </div>
            <p className="text-xs text-amber-200/90 leading-relaxed font-medium">
              {nodeData.dependency_reason}
            </p>
          </div>
        )}

        {/* Existing Baseline Hardware */}
        {nodeData.baseline_name && (
          <div className="rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt p-3 text-xs flex items-center justify-between">
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
              Current Installed
            </span>
            <span className="font-semibold text-slate-200 truncate ml-2">
              {nodeData.baseline_name}
            </span>
          </div>
        )}

        {/* Price Card */}
        {typeof nodeData.price === 'number' && (
          <div className="rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-mono">
                {nodeData.status === 'reusable' || nodeData.upgrade_role === 'retained' ? 'Retained Cost' : 'Recorded INR Price'}
              </div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                {nodeData.status === 'reusable' || nodeData.upgrade_role === 'retained' ? '₹0 (Installed)' : `₹${nodeData.price.toLocaleString()}`}
              </div>
            </div>
            {nodeData.seller && (
              <div className="text-right">
                <div className="text-[10px] text-slate-500">Retailer</div>
                <div className="text-xs font-medium text-slate-300 flex items-center gap-1 justify-end">
                  <Store size={12} className="text-slate-400" />
                  {nodeData.seller}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Source & Availability */}
        {nodeData.priceBasis && (
          <div className="text-[11px] text-slate-400 bg-canvas-panelAlt/60 rounded-lg p-2.5 border border-canvas-border/70 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Price Basis:</span>
              <span className="text-slate-300 font-medium">{nodeData.priceBasis}</span>
            </div>
            {nodeData.availability && (
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Stock Availability:</span>
                <span className="text-emerald-400 capitalize font-medium">{nodeData.availability}</span>
              </div>
            )}
            {nodeData.sourceUrl && (
              <div className="pt-1">
                <a
                  href={nodeData.sourceUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent-soft hover:underline flex items-center gap-1 text-[10px]"
                >
                  <ExternalLink size={10} /> View verified store listing
                </a>
              </div>
            )}
          </div>
        )}

        {/* Supervised ML Performance Prediction */}
        {nodeData.mlPrediction && (
          <div className="rounded-xl border border-indigo-500/30 bg-gradient-to-br from-canvas-panelAlt to-indigo-950/30 p-3.5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-mono tracking-wider text-indigo-300 font-semibold flex items-center gap-1.5">
                <Sparkles size={12} className="text-indigo-400" /> Supervised ML Estimate
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-200 font-mono">
                Ridge Model
              </span>
            </div>
            {nodeData.mlPrediction.status === 'success' && nodeData.mlPrediction.score ? (
              <div>
                <div className="text-lg font-bold font-mono text-indigo-200">
                  {nodeData.mlPrediction.score.toLocaleString()} pts
                </div>
                <div className="text-[11px] text-indigo-300/80">
                  {nodeData.mlPrediction.metric}
                </div>
              </div>
            ) : (
              <div className="text-xs text-amber-300/90">
                {nodeData.mlPrediction.reason || 'Estimate unavailable for this configuration'}
              </div>
            )}
          </div>
        )}

        {/* Recorded Empirical Benchmark */}
        {nodeData.empiricalBenchmark && (
          <div className="rounded-xl border border-emerald-500/30 bg-gradient-to-br from-canvas-panelAlt to-emerald-950/20 p-3.5 space-y-1">
            <div className="text-[10px] uppercase font-mono tracking-wider text-emerald-400 font-semibold flex items-center gap-1.5">
              <CheckCircle2 size={12} /> Recorded Empirical Benchmark
            </div>
            <div className="text-lg font-bold font-mono text-emerald-300">
              {nodeData.empiricalBenchmark.score.toLocaleString()} pts
            </div>
            <div className="text-[11px] text-slate-400">
              {nodeData.empiricalBenchmark.metric} · {nodeData.empiricalBenchmark.source}
            </div>
          </div>
        )}

        {/* AI Selection Reasoning */}
        {nodeData.reason && (
          <div className="rounded-xl border border-canvas-borderAlt bg-canvas-panelAlt p-3">
            <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold mb-1 flex items-center gap-1">
              <Brain size={12} className="text-accent-soft" /> Recommender Reasoning
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{nodeData.reason}</p>
          </div>
        )}

        {/* Detailed Hardware Specifications */}
        {nodeData.specs && Object.keys(nodeData.specs).length > 0 && (
          <div className="space-y-2">
            <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold">
              Hardware Specifications
            </div>
            <div className="rounded-xl border border-canvas-border bg-canvas-panelAlt divide-y divide-canvas-border/80">
              {Object.entries(nodeData.specs).map(([key, val]) => (
                <div key={key} className="px-3 py-1.5 flex items-center justify-between text-xs">
                  <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="font-mono text-slate-200 truncate ml-2 max-w-[55%] text-right">
                    {String(val)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Validation Checks */}
        {nodeData.checks && nodeData.checks.length > 0 && (
          <div className="space-y-2">
            <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
              <ShieldCheck size={12} className="text-emerald-400" /> Compatibility Findings ({nodeData.checks.length})
            </div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {nodeData.checks.map((chk, idx) => (
                <div
                  key={idx}
                  className={`p-2.5 rounded-lg border text-[11px] ${
                    chk.status === 'compatible'
                      ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-200'
                      : chk.status === 'incompatible'
                      ? 'border-red-500/30 bg-red-950/20 text-red-200'
                      : 'border-slate-700 bg-slate-900/40 text-slate-300'
                  }`}
                >
                  <div className="font-semibold flex items-center justify-between mb-0.5">
                    <span>{chk.pair}</span>
                    <span className="capitalize text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/30">
                      {chk.status}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 leading-tight">{chk.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alternative Component Choices */}
        {isComponent && nodeData.alternatives && nodeData.alternatives.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-canvas-border">
            <button
              onClick={() => setShowAlternatives(!showAlternatives)}
              className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-canvas-panelAlt border border-canvas-border hover:border-accent/40 text-xs font-semibold text-slate-200 transition"
            >
              <span className="flex items-center gap-2">
                <RefreshCw size={13} className="text-accent-soft" />
                Compatible Alternatives ({nodeData.alternatives.length})
              </span>
              {showAlternatives ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showAlternatives && (
              <div className="space-y-2 animate-fadeIn">
                <p className="text-[11px] text-slate-400">
                  Select an alternative candidate. Compatibility and budget will be dynamically re-evaluated:
                </p>
                {nodeData.alternatives.map((alt) => (
                  <div
                    key={alt.id}
                    className="p-3 rounded-xl border border-canvas-border hover:border-accent/50 bg-canvas-panelAlt transition flex flex-col gap-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-slate-200 truncate">{alt.name}</div>
                        <div className="text-[10px] text-slate-400">{alt.brand}</div>
                      </div>
                      <div className="text-xs font-bold font-mono text-emerald-400 shrink-0">
                        {alt.price ? `₹${alt.price.toLocaleString()}` : 'Price unlisted'}
                      </div>
                    </div>

                    <button
                      disabled={isReplacing}
                      onClick={() => onReplaceComponent(nodeData.category || '', alt.id)}
                      className="w-full py-1.5 px-3 rounded-lg bg-accent/20 hover:bg-accent text-accent-soft hover:text-white border border-accent/40 text-xs font-semibold transition disabled:opacity-50 flex items-center justify-center gap-1.5"
                    >
                      {isReplacing ? (
                        <>
                          <RefreshCw size={12} className="animate-spin" />
                          Revalidating...
                        </>
                      ) : (
                        'Swap This Component'
                      )}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
};
