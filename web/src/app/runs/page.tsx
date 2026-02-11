"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type {
  EvalModel,
  EvalRun,
  BenchmarkSuite,
  TaskResult,
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

function scoreColor(score?: number): string {
  if (score == null) return "text-slate-500";
  if (score >= 70) return "text-green-400";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

function formatDuration(start?: string, end?: string): string {
  if (!start) return "--";
  const s = new Date(start).getTime();
  const e = end ? new Date(end).getTime() : Date.now();
  const sec = Math.round((e - s) / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  return `${min}m ${sec % 60}s`;
}

export default function RunsPage() {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

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

  // Poll for active runs
  useEffect(() => {
    const hasActive = runs.some((r) =>
      ["pending", "queued", "running"].includes(r.status)
    );
    if (!hasActive) return;
    const timer = setInterval(fetchRuns, 3000);
    return () => clearInterval(timer);
  }, [runs]);

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
      setError(err instanceof Error ? err.message : "Failed to load form data");
    }
  }

  async function handleNewRun(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedModel || !selectedSuite) return;
    setSubmitting(true);
    try {
      await api.startRun({ model_id: selectedModel, suite_id: selectedSuite });
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

  async function handleCancel(runId: string) {
    try {
      await api.cancelRun(runId);
      fetchRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel run");
    }
  }

  async function handleRerun(run: EvalRun) {
    try {
      await api.startRun({ model_id: run.model_id, suite_id: run.suite_id });
      fetchRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to re-run");
    }
  }

  function toggleExpand(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Evaluation Runs</h1>
        <button
          onClick={() => { setShowNewRun(true); loadFormData(); }}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 transition-colors"
        >
          New Run
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-red-200">Dismiss</button>
        </div>
      )}

      {/* New run form */}
      {showNewRun && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Start New Run</h3>
          <form onSubmit={handleNewRun} className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">Model</label>
              <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none" required>
                <option value="">Select a model...</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>{m.name} ({m.model_type.toUpperCase()})</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">Suite</label>
              <select value={selectedSuite} onChange={(e) => setSelectedSuite(e.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none" required>
                <option value="">Select a suite...</option>
                {suites.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <button type="submit" disabled={submitting || !selectedModel || !selectedSuite} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors">
              {submitting ? "Starting..." : "Start Run"}
            </button>
            <button type="button" onClick={() => setShowNewRun(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors">
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
                    <th className="text-left px-5 py-3 font-medium">Progress</th>
                    <th className="text-left px-5 py-3 font-medium">Score</th>
                    <th className="text-left px-5 py-3 font-medium">Date</th>
                    <th className="text-left px-5 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => (
                    <RunRow
                      key={run.id}
                      run={run}
                      expanded={expandedId === run.id}
                      onToggle={() => toggleExpand(run.id)}
                      onCancel={() => handleCancel(run.id)}
                      onRerun={() => handleRerun(run)}
                    />
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

// ── Expandable run row ───────────────────────────────────────

function RunRow({
  run,
  expanded,
  onToggle,
  onCancel,
  onRerun,
}: {
  run: EvalRun;
  expanded: boolean;
  onToggle: () => void;
  onCancel: () => void;
  onRerun: () => void;
}) {
  const [results, setResults] = useState<TaskResult[]>([]);
  const [loadingResults, setLoadingResults] = useState(false);

  useEffect(() => {
    if (!expanded) return;
    setLoadingResults(true);
    api
      .getRunResults(run.id)
      .then((res) => setResults(res.items))
      .catch(() => setResults([]))
      .finally(() => setLoadingResults(false));
  }, [expanded, run.id]);

  const isActive = ["pending", "queued", "running"].includes(run.status);
  const isTerminal = ["completed", "failed", "cancelled"].includes(run.status);

  return (
    <>
      <tr
        className={`border-b border-slate-800/50 cursor-pointer transition-colors ${
          expanded ? "bg-slate-800/40" : "hover:bg-slate-800/30"
        }`}
        onClick={onToggle}
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
                style={{ width: `${run.progress_percent ?? 0}%` }}
              />
            </div>
            <span className="text-xs text-slate-500">
              {run.tasks_completed}/{run.tasks_total}
            </span>
          </div>
        </td>
        <td className={`px-5 py-3 font-mono ${scoreColor(run.overall_score)}`}>
          {run.overall_score != null ? run.overall_score.toFixed(1) : "--"}
        </td>
        <td className="px-5 py-3 text-slate-400">
          {run.created_at ? new Date(run.created_at).toLocaleDateString() : "--"}
        </td>
        <td className="px-5 py-3">
          <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
            {isActive && (
              <button
                onClick={onCancel}
                className="rounded-lg border border-red-500/30 bg-red-500/10 px-2.5 py-1 text-xs text-red-400 hover:bg-red-500/20 transition-colors"
              >
                Cancel
              </button>
            )}
            {isTerminal && (
              <button
                onClick={onRerun}
                className="rounded-lg border border-blue-500/30 bg-blue-500/10 px-2.5 py-1 text-xs text-blue-400 hover:bg-blue-500/20 transition-colors"
              >
                Re-run
              </button>
            )}
          </div>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={7} className="bg-slate-800/20 px-5 py-4">
            <RunDetail
              run={run}
              results={results}
              loading={loadingResults}
            />
          </td>
        </tr>
      )}
    </>
  );
}

// ── Run detail panel ─────────────────────────────────────────

function RunDetail({
  run,
  results,
  loading,
}: {
  run: EvalRun;
  results: TaskResult[];
  loading: boolean;
}) {
  return (
    <div className="space-y-4">
      {/* Run metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <span className="text-slate-500">Model</span>
          <p className="text-slate-200 mt-0.5">{run.model_name ?? run.model_id}</p>
        </div>
        <div>
          <span className="text-slate-500">Suite</span>
          <p className="text-slate-200 mt-0.5">{run.suite_name ?? run.suite_id}</p>
        </div>
        <div>
          <span className="text-slate-500">Duration</span>
          <p className="text-slate-200 mt-0.5">
            {formatDuration(run.started_at, run.completed_at)}
          </p>
        </div>
        <div>
          <span className="text-slate-500">Triggered by</span>
          <p className="text-slate-200 mt-0.5">{run.triggered_by}</p>
        </div>
      </div>

      {/* Task results table */}
      <div>
        <h4 className="text-xs font-medium text-slate-400 mb-2">
          Task Results ({results.length})
        </h4>
        {loading ? (
          <p className="text-xs text-slate-500">Loading results...</p>
        ) : results.length === 0 ? (
          <p className="text-xs text-slate-500">No task results available.</p>
        ) : (
          <div className="rounded-lg border border-slate-700/50 overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/50 text-slate-500">
                  <th className="text-left px-3 py-2 font-medium">Task</th>
                  <th className="text-left px-3 py-2 font-medium">Tier</th>
                  <th className="text-left px-3 py-2 font-medium">Score</th>
                  <th className="text-left px-3 py-2 font-medium">Raw</th>
                  <th className="text-left px-3 py-2 font-medium">Latency</th>
                  <th className="text-left px-3 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-slate-700/30 last:border-0"
                  >
                    <td className="px-3 py-2 text-slate-300">
                      {r.task_name ?? r.task_id}
                    </td>
                    <td className="px-3 py-2 text-slate-400">
                      {r.education_tier ?? "--"}
                    </td>
                    <td className={`px-3 py-2 font-mono ${scoreColor(r.score)}`}>
                      {r.score != null ? r.score.toFixed(1) : "--"}
                    </td>
                    <td className="px-3 py-2 text-slate-400 font-mono">
                      {r.raw_score != null
                        ? `${r.raw_score.toFixed(4)} (${r.raw_metric_name ?? "?"})`
                        : "--"}
                    </td>
                    <td className="px-3 py-2 text-slate-400">
                      {r.latency_ms != null ? `${r.latency_ms}ms` : "--"}
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${
                          statusStyles[r.status] ?? statusStyles.pending
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
