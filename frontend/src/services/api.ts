import {
  BuildRequest,
  CatalogSummary,
  HistoryItem,
  Project,
  UpgradeRequest,
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMsg = `Request failed with status ${res.status}`;
    try {
      const errData = await res.json();
      if (errData.detail) errMsg = errData.detail;
      else if (errData.message) errMsg = errData.message;
    } catch {
      // ignore json parse error
    }
    throw new Error(errMsg);
  }
  return res.json();
}

export const api = {
  async getHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async getCatalogSummary(): Promise<CatalogSummary> {
    const res = await fetch(`${API_BASE}/catalog/summary`);
    return handleResponse<CatalogSummary>(res);
  },

  async getComponents(category?: string, query?: string, limit = 50): Promise<any[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (query) params.append('query', query);
    params.append('limit', limit.toString());
    const res = await fetch(`${API_BASE}/catalog/components?${params.toString()}`);
    return handleResponse(res);
  },

  async recommendBuild(payload: BuildRequest): Promise<Project> {
    const res = await fetch(`${API_BASE}/build/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Project>(res);
  },

  async recommendUpgrade(payload: UpgradeRequest): Promise<Project> {
    const res = await fetch(`${API_BASE}/upgrade/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Project>(res);
  },

  async replaceComponent(projectId: string, category: string, newComponentId: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/workflow/${projectId}/replace-component`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, new_component_id: newComponentId }),
    });
    return handleResponse<Project>(res);
  },

  async getProjects(mode?: string): Promise<Project[]> {
    const url = mode ? `${API_BASE}/projects?mode=${mode}` : `${API_BASE}/projects`;
    const res = await fetch(url);
    return handleResponse<Project[]>(res);
  },

  async getProject(projectId: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${projectId}`);
    return handleResponse<Project>(res);
  },

  async saveProject(project: Partial<Project>): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project),
    });
    return handleResponse<Project>(res);
  },

  async deleteProject(projectId: string): Promise<{ status: string; id: string }> {
    const res = await fetch(`${API_BASE}/projects/${projectId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  async getHistory(): Promise<HistoryItem[]> {
    const res = await fetch(`${API_BASE}/history`);
    return handleResponse<HistoryItem[]>(res);
  },

  async downloadProjectPdf(projectId: string, projectName?: string): Promise<void> {
    const res = await fetch(`${API_BASE}/export/${projectId}/pdf`);
    if (!res.ok) {
      throw new Error(`Failed to download PDF report (${res.status})`);
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeName = (projectName || projectId).replace(/[^a-zA-Z0-9_\-]/g, '_');
    a.download = `${safeName}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  async downloadProjectCsv(projectId: string, projectName?: string): Promise<void> {
    const res = await fetch(`${API_BASE}/export/${projectId}/csv`);
    if (!res.ok) {
      throw new Error(`Failed to download CSV report (${res.status})`);
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeName = (projectName || projectId).replace(/[^a-zA-Z0-9_\-]/g, '_');
    a.download = `${safeName}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },
};
