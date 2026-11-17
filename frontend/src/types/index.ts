export type NodeKind =
  | 'requirements'
  | 'budget'
  | 'ai'
  | 'component'
  | 'compat'
  | 'analysis'
  | 'final'
  | 'existing';

export type NodeStatus =
  | 'pending'
  | 'recommended'
  | 'selected'
  | 'compatible'
  | 'incompatible'
  | 'existing'
  | 'reusable'
  | 'warning'
  | 'dependency';

export type ComponentCategory =
  | 'cpu'
  | 'motherboard'
  | 'ram'
  | 'gpu'
  | 'storage'
  | 'psu'
  | 'case'
  | 'cooler';

export interface EmpiricalBenchmark {
  metric: string;
  score: number;
  source: string;
  recorded_at?: string;
}

export interface MLPrediction {
  metric: string;
  score?: number;
  model?: string;
  status: 'success' | 'unavailable' | 'extrapolation_limit';
  reason?: string;
}

export interface ComponentAlternative {
  id: string;
  name: string;
  brand: string;
  price?: number;
  specs: Record<string, any>;
}

export interface WorkflowNodeData {
  [key: string]: any;
  kind: NodeKind;
  category?: ComponentCategory;
  label: string;
  subtitle?: string;
  description?: string;
  status?: NodeStatus;
  upgrade_role?: 'primary' | 'dependency' | 'retained' | 'optional' | 'unresolved';
  dependency_reason?: string;
  baseline_name?: string;
  price?: number;
  specs?: Record<string, any>;
  componentId?: string;
  seller?: string;
  sourceUrl?: string;
  availability?: string;
  priceBasis?: string;
  empiricalBenchmark?: EmpiricalBenchmark | null;
  mlPrediction?: MLPrediction | null;
  alternatives?: ComponentAlternative[];
  reason?: string;
  checks?: Array<{ pair: string; status: string; reason: string }>;
}

export interface WorkflowSummary {
  total: number;
  budget: number;
  remaining: number;
  status: 'compatible' | 'incompatible' | 'warning' | 'insufficient_budget';
  validationStatus?: string;
  checksCount?: number;
  notes?: string[];
  goal?: string;
  upgradedCategories?: string[];
  primaryCategories?: string[];
  dependentCategories?: string[];
  retainedCategories?: string[];
  unresolvedCategories?: string[];
  upgradeRoles?: Record<string, string>;
  deltas?: Record<string, {
    metric: string;
    baselineScore: number;
    upgradeScore: number;
    absoluteDelta: number;
    percentageDelta: number;
  }>;
}

export interface Project {
  id: string;
  mode: 'build' | 'upgrade';
  name: string;
  createdAt: string;
  updatedAt: string;
  inputs: Record<string, any>;
  recommendationSnapshot?: any;
  nodes: any[];
  edges: any[];
  summary: WorkflowSummary;
  componentCount?: number;
}

export interface CatalogSummary {
  components_count: number;
  prices_count: number;
  benchmarks_count: number;
  priced_components_count: number;
  cpu_models_available: boolean;
  gpu_models_available: boolean;
  categories: Record<string, number>;
}

export interface BuildRequest {
  usage: string;
  budget: number;
}

export interface UpgradeRequest {
  existing: Record<string, string>;
  budget: number;
  goal: string;
}

export interface HistoryItem {
  id: string;
  projectId: string;
  mode: string;
  createdAt: string;
  inputs: Record<string, any>;
  summary: WorkflowSummary;
}
