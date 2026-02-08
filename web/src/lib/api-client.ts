// ──────────────────────────────────────────────────────────────
// Typed fetch wrapper for the FastAPI evaluation backend.
// All requests are proxied through Next.js at /api/eval/*.
// ──────────────────────────────────────────────────────────────

import type {
  EvalModel,
  BenchmarkSuite,
  EvalRun,
  TaskResult,
  PaginatedResponse,
} from "@/types/evaluation";

const BASE = "/api/eval";

/**
 * Generic JSON fetcher with error handling.
 * Throws with the `detail` field from the API error body when available.
 */
async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    const err: { detail?: string } = await res
      .json()
      .catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ── Public API surface ───────────────────────────────────────

export const api = {
  // ── Models ───────────────────────────────────────────────

  listModels: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchJson<PaginatedResponse<EvalModel>>(`/models${qs}`);
  },

  getModel: (id: string) => fetchJson<EvalModel>(`/models/${id}`),

  createModel: (data: Partial<EvalModel>) =>
    fetchJson<EvalModel>("/models", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteModel: (id: string) =>
    fetchJson<void>(`/models/${id}`, { method: "DELETE" }),

  importHuggingFace: (data: {
    repo_id: string;
    model_type: string;
    deployment_target?: string;
  }) =>
    fetchJson<EvalModel>("/models/import-hf", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // ── Suites ───────────────────────────────────────────────

  listSuites: () =>
    fetchJson<{ items: BenchmarkSuite[]; total: number }>("/suites"),

  getSuite: (id: string) => fetchJson<BenchmarkSuite>(`/suites/${id}`),

  // ── Runs ─────────────────────────────────────────────────

  listRuns: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchJson<PaginatedResponse<EvalRun>>(`/runs${qs}`);
  },

  getRun: (id: string) => fetchJson<EvalRun>(`/runs/${id}`),

  startRun: (data: {
    model_id: string;
    suite_id: string;
    config?: Record<string, any>;
  }) =>
    fetchJson<{ run_id: string }>("/runs", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  cancelRun: (id: string) =>
    fetchJson<void>(`/runs/${id}/cancel`, { method: "POST" }),

  getRunResults: (id: string) =>
    fetchJson<{ items: TaskResult[] }>(`/runs/${id}/results`),

  // ── Grade Matrix ─────────────────────────────────────────

  getGradeMatrix: (modelId?: string) => {
    const qs = modelId ? `?model_id=${modelId}` : "";
    return fetchJson<{ matrix: any[] }>(`/grade-matrix${qs}`);
  },

  // ── Compare ──────────────────────────────────────────────

  compareRuns: (runIds: string[]) =>
    fetchJson<{ comparisons: any[] }>(
      `/compare?run_ids=${runIds.join(",")}`
    ),

  compareModels: (modelIds: string[], suiteId?: string) => {
    let qs = `model_ids=${modelIds.join(",")}`;
    if (suiteId) qs += `&suite_id=${suiteId}`;
    return fetchJson<{ comparisons: any[] }>(`/compare/models?${qs}`);
  },

  // ── Trends ───────────────────────────────────────────────

  getTrends: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchJson<{ trends: Record<string, any[]> }>(`/trends${qs}`);
  },

  // ── Baselines ────────────────────────────────────────────

  listBaselines: () => fetchJson<{ items: any[] }>("/baselines"),

  // ── Test sets ────────────────────────────────────────────

  listTestSets: () => fetchJson<{ items: any[] }>("/test-sets"),

  // ── Export / Import ──────────────────────────────────────

  exportData: (data: {
    run_ids?: string[];
    model_id?: string;
    format?: string;
  }) =>
    fetchJson<void>("/export", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  importData: (data: Record<string, any>) =>
    fetchJson<void>("/import", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // ── Share ────────────────────────────────────────────────

  listSharedLinks: () =>
    fetchJson<Array<{ id: string; url: string; label: string; created_at: string }>>(
      "/shared-links"
    ),

  createShare: (data: {
    report_type: string;
    report_config: Record<string, any>;
    expires_in_days?: number;
  }) =>
    fetchJson<{ token: string; url: string }>("/share", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteSharedLink: (id: string) =>
    fetchJson<void>(`/shared-links/${id}`, { method: "DELETE" }),

  // ── Health ───────────────────────────────────────────────

  health: () =>
    fetchJson<{ status: string; version: string }>("/health"),
} as const;
