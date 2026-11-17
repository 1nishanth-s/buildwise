import React, { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
  BackgroundVariant,
  Node,
  Edge,
} from '@xyflow/react';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Cpu,
  Download,
  FileSpreadsheet,
  FileText,
  Loader2,
  Save,
  Share2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Wallet,
} from 'lucide-react';
import { api } from '../services/api';
import { Project, WorkflowNodeData } from '../types';
import { WorkflowNode } from '../components/nodes/WorkflowNode';
import { PropertiesPanel } from '../components/panels/PropertiesPanel';

const nodeTypes = {
  workflowNode: WorkflowNode as any,
};

export const WorkflowCanvas: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [replacing, setReplacing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const [downloadingCsv, setDownloadingCsv] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  // Load project on mount or ID change
  useEffect(() => {
    async function fetchProject() {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const proj = await api.getProject(id);
        setProject(proj);
        setNodes(proj.nodes || []);
        setEdges(proj.edges || []);
        // Auto-select first component node
        const firstComp = proj.nodes.find((n: any) => n.data?.kind === 'component');
        if (firstComp) {
          setSelectedNodeId(firstComp.id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load workflow project.');
      } finally {
        setLoading(false);
      }
    }
    fetchProject();
  }, [id]);

  // Handle node position changes
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    []
  );

  // Handle edge changes
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
    },
    []
  );

  // Handle node click
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  // Handle canvas pane click to deselect
  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  // Handle dynamic component replacement
  const handleReplaceComponent = async (category: string, newComponentId: string) => {
    if (!project || !id) return;
    setReplacing(true);
    try {
      const updated = await api.replaceComponent(id, category, newComponentId);
      setProject(updated);
      setNodes(updated.nodes || []);
      setEdges(updated.edges || []);
      // Reselect the swapped node
      const updatedComp = updated.nodes.find(
        (n: any) => n.data?.kind === 'component' && n.data?.category === category
      );
      if (updatedComp) {
        setSelectedNodeId(updatedComp.id);
      }
    } catch (err: any) {
      alert(`Replacement failed: ${err.message}`);
    } finally {
      setReplacing(false);
    }
  };

  // Save project positions & state
  const handleSaveProject = async () => {
    if (!project) return;
    setSaving(true);
    try {
      const updated = await api.saveProject({
        ...project,
        nodes,
        edges,
      });
      setProject(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err: any) {
      alert(`Save failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!project) return;
    try {
      setDownloadingPdf(true);
      setDownloadError(null);
      await api.downloadProjectPdf(project.id, project.name);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to download PDF report');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadCsv = async () => {
    if (!project) return;
    try {
      setDownloadingCsv(true);
      setDownloadError(null);
      await api.downloadProjectCsv(project.id, project.name);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to download CSV report');
    } finally {
      setDownloadingCsv(false);
    }
  };

  // Currently selected node data
  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const selectedNodeData = (selectedNode?.data as WorkflowNodeData) || null;

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-canvas-bg text-slate-400 gap-3">
        <Sparkles size={32} className="animate-spin text-accent-soft" />
        <p className="text-sm font-medium">Loading AI recommendation workflow canvas...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-canvas-bg text-slate-400 p-8 text-center">
        <AlertCircle size={36} className="text-red-400 mb-3" />
        <h2 className="text-lg font-bold text-slate-200">Workflow Project Not Found</h2>
        <p className="text-xs text-slate-400 mt-1 max-w-md">{error || 'Unable to load project data.'}</p>
        <button
          onClick={() => navigate('/')}
          className="mt-5 px-4 py-2 rounded-xl bg-accent text-white text-xs font-semibold hover:bg-accent-dim transition"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const summary = project.summary;
  const isOverBudget = summary.remaining < 0;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-canvas-bg">
      {/* Top Workflow Action Bar */}
      <div className="h-14 border-b border-canvas-border bg-canvas-panel px-6 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-1.5 rounded-lg border border-canvas-border text-slate-400 hover:text-slate-200 hover:bg-canvas-panelAlt transition"
            title="Back to Dashboard"
          >
            <ArrowLeft size={16} />
          </button>

          <div>
            <div className="flex items-center gap-2">
              <span
                className={`text-[9px] uppercase font-mono px-2 py-0.5 rounded font-bold ${
                  project.mode === 'build'
                    ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                    : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                }`}
              >
                {project.mode} workflow
              </span>
              <h1 className="text-sm font-bold text-slate-100 truncate max-w-xs md:max-w-md">
                {project.name}
              </h1>
            </div>
          </div>
        </div>

        {/* Budget Tracker Pill */}
        <div className="hidden lg:flex items-center gap-6 px-4 py-1.5 rounded-xl bg-canvas-panelAlt border border-canvas-border font-mono text-xs">
          <div>
            <span className="text-[10px] uppercase text-slate-500 block">Total Price</span>
            <span className="font-bold text-emerald-400">₹{summary.total.toLocaleString()}</span>
          </div>
          <div className="h-6 w-px bg-canvas-border" />
          <div>
            <span className="text-[10px] uppercase text-slate-500 block">Target Budget</span>
            <span className="font-semibold text-slate-300">₹{summary.budget.toLocaleString()}</span>
          </div>
          <div className="h-6 w-px bg-canvas-border" />
          <div>
            <span className="text-[10px] uppercase text-slate-500 block">Remaining</span>
            <span className={`font-semibold ${isOverBudget ? 'text-amber-400' : 'text-slate-300'}`}>
              ₹{summary.remaining.toLocaleString()}
            </span>
          </div>
          <div className="h-6 w-px bg-canvas-border" />
          <div className="flex items-center gap-1.5">
            {summary.status === 'compatible' ? (
              <span className="flex items-center gap-1 text-[11px] font-sans font-semibold text-emerald-400">
                <ShieldCheck size={14} /> Compatible
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[11px] font-sans font-semibold text-amber-400">
                <ShieldAlert size={14} /> Review Needed
              </span>
            )}
          </div>
        </div>

        {/* Top Actions */}
        <div className="flex items-center gap-2">
          {downloadError && (
            <span className="text-[11px] text-red-400 mr-2 flex items-center gap-1 font-sans">
              <AlertCircle size={12} /> {downloadError}
            </span>
          )}

          <button
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            title="Download PDF Recommendation Report"
            className="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 bg-canvas-panelAlt hover:bg-slate-800 text-slate-200 border border-canvas-border hover:border-slate-700 transition shadow-sm disabled:opacity-50"
          >
            {downloadingPdf ? (
              <Loader2 size={14} className="animate-spin text-accent" />
            ) : (
              <FileText size={14} className="text-rose-400" />
            )}
            <span>PDF</span>
          </button>

          <button
            onClick={handleDownloadCsv}
            disabled={downloadingCsv}
            title="Download Excel-Compatible CSV Spreadsheet"
            className="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 bg-canvas-panelAlt hover:bg-slate-800 text-slate-200 border border-canvas-border hover:border-slate-700 transition shadow-sm disabled:opacity-50"
          >
            {downloadingCsv ? (
              <Loader2 size={14} className="animate-spin text-accent" />
            ) : (
              <FileSpreadsheet size={14} className="text-emerald-400" />
            )}
            <span>CSV</span>
          </button>

          <button
            onClick={handleSaveProject}
            disabled={saving}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
              saveSuccess
                ? 'bg-emerald-500 text-white'
                : 'bg-accent hover:bg-accent-dim text-white shadow-sm shadow-accent/20'
            }`}
          >
            {saveSuccess ? (
              <>
                <CheckCircle2 size={14} /> Saved
              </>
            ) : (
              <>
                <Save size={14} /> {saving ? 'Saving...' : 'Save Plan'}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Canvas Workspace with Central Editor and Right Properties Panel */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Central React Flow Editor Canvas */}
        <div className="flex-1 h-full relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.12 }}
            minZoom={0.2}
            maxZoom={1.8}
            defaultViewport={{ x: 50, y: 50, zoom: 0.85 }}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#1f2937" gap={24} size={1.5} variant={BackgroundVariant.Dots} />
            <Controls className="bg-canvas-panel border-canvas-border text-slate-300 rounded-xl" />
            <MiniMap
              nodeColor={(n: any) => {
                if (n.data?.kind === 'component') return '#6366f1';
                if (n.data?.kind === 'compat') return '#10b981';
                if (n.data?.kind === 'existing') return '#06b6d4';
                return '#334155';
              }}
              className="bg-canvas-panel border-canvas-border rounded-xl"
              maskColor="rgba(10, 14, 26, 0.7)"
            />
          </ReactFlow>
        </div>

        {/* Right Properties Panel */}
        <PropertiesPanel
          nodeData={selectedNodeData}
          onClose={() => setSelectedNodeId(null)}
          onReplaceComponent={handleReplaceComponent}
          isReplacing={replacing}
        />
      </div>
    </div>
  );
};
