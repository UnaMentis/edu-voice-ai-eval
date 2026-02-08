"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type {
  EvalModel,
  EvalRun,
  BenchmarkSuite,
  RunStatus,
} from "@/types/evaluation";

const STATUS_FILTERS: Array<{ label: string; value: string }> = [
  { label: "All", value: "all" },
  { label: "Running", value: "running" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
  { label: "Pending", value: "pending" },
];

const statusStyles: Record<string, string> = {
  completed: "bg-green-500/15 text-green-400 border-green-500/30",
  running: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  pending: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  queued: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  failed: "bg-red-500/15 text-red-400 border-red-500/30",
  cancelled: "bg-slate-500/15 text-slate-500 border-slate-500/30",
};

export default function RunsPage() {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New run form
  const [showNewRun, setShowNewRun] = useState(false);
  const [models, setModels] = useState<EvalModel[]>([]);
  const [suites, setSuites] = useState<BenchmarkSuite[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedSuite, setSelectedSuite] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchRuns();
  }, [statusFilter]);

  async function fetchRuns() {
    setLoading(true);
    try {
      const params: Record<string, string> =
        statusFilter !== "all" ? { status: statusFilter } : {};
      const res = await api.listRuns(params);
      setRuns(res.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load runs");
    } finally {
      setLoading(false);
    }
  }

  async function loadFormData() {
    try {
      const [modelsRes, suitesRes] = await Promise.all([
        api.listModels(),
        api.listSuites(),
      ]);
      setModels(modelsRes.items);
      setSuites(suitesRes.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load form data"
      );
    }
  }

  async function handleNewRun(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedModel || !selectedSuite) return;
    setSubmitting(true);
    try {
      await api.startRun({
        model_id: selectedModel,
        suite_id: selectedSuite,
      });
      setShowNewRun(false);
      setSelectedModel("");
      setSelectedSuite("");
      fetchRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start run");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Evaluation Runs</h1>
        <button
          onClick={() => {
            setShowNewRun(true);
            loadFormData();
          }}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 transition-colors"
        >
          New Run
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-300 hover:text-red-200"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* New run form */}
      {showNewRun && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">
            Start New Run
          </h3>
          <form onSubmit={handleNewRun} className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">
                Model
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
                required
              >
                <option value="">Select a model...</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.model_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">
                Suite
              </label>
              <select
                value={selectedSuite}
                onChange={(e) => setSelectedSuite(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
                required
              >
                <option value="">Select a suite...</option>
                {suites.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={submitting || !selectedModel || !selectedSuite}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
            >
              {submitting ? "Starting..." : "Start Run"}
            </button>
            <button
              type="button"
              onClick={() => setShowNewRun(false)}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Status filter */}
      <div className="flex gap-2 mb-6">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              statusFilter === f.value
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Runs table */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-slate-400">Loading runs...</p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
          {runs.length === 0 ? (
            <div className="px-5 py-12 text-center">
              <p className="text-slate-500 text-lg mb-1">No runs found</p>
              <p className="text-slate-600 text-sm">
                {statusFilter !== "all"
                  ? `No ${statusFilter} runs. Try a different filter.`
                  : "Start a new evaluation run to see results here."}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="text-left px-5 py-3 font-medium">Model</th>
                    <th className="text-left px-5 py-3 font-medium">Suite</th>
                    <th className="text-left px-5 py-3 font-medium">Status</th>
                    <th className="text-left px-5 py-3 font-medium">
                      Progress
                    </th>
                    <th className="text-left px-5 py-3 font-medium">Score</th>
                    <th className="text-left px-5 py-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => (
                    <tr
                      key={run.id}
                      className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="px-5 py-3 text-slate-200">
                        {run.model_name ?? run.model_id}
                      </td>
                      <td className="px-5 py-3 text-slate-300">
                        {run.suite_name ?? run.suite_id}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${
                            statusStyles[run.status] ?? statusStyles.pending
                          }`}
                        >
                          {run.status}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-20 rounded-full bg-slate-800 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-blue-500 transition-all"
                              style={{
                                width: `${run.progress_percent ?? 0}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs text-slate-500">
                            {run.tasks_completed}/{run.tasks_total}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3 text-slate-200 font-mono">
                        {run.overall_score != null
                          ? run.overall_score.toFixed(1)
                          : "--"}
                      </td>
                      <td className="px-5 py-3 text-slate-400">
                        {run.created_at
                          ? new Date(run.created_at).toLocaleDateString()
                          : "--"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
