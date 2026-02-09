"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api-client";
import type { BenchmarkSuite } from "@/types/evaluation";

const typeColors: Record<string, string> = {
  llm: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  stt: "bg-green-500/15 text-green-400 border-green-500/30",
  tts: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  vad: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  mixed: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
};

interface SuiteTask {
  id: string;
  name: string;
  task_type: string;
  education_tier?: string;
  subject?: string;
  weight: number;
}

export default function BenchmarksPage() {
  const [suites, setSuites] = useState<BenchmarkSuite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create modal
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: "",
    model_type: "llm",
    description: "",
    category: "",
  });
  const [creating, setCreating] = useState(false);

  // Detail panel
  const [selectedSuite, setSelectedSuite] = useState<string | null>(null);
  const [suiteTasks, setSuiteTasks] = useState<SuiteTask[]>([]);
  const [loadingTasks, setLoadingTasks] = useState(false);

  const loadSuites = useCallback(async () => {
    try {
      const res = await api.listSuites();
      setSuites(res.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load suites");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSuites();
  }, [loadSuites]);

  // Load tasks when a suite is selected
  useEffect(() => {
    if (!selectedSuite) {
      setSuiteTasks([]);
      return;
    }
    setLoadingTasks(true);
    api
      .getSuiteTasks(selectedSuite)
      .then((res) => setSuiteTasks(res.items))
      .catch(() => setSuiteTasks([]))
      .finally(() => setLoadingTasks(false));
  }, [selectedSuite]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!createForm.name.trim()) return;
    setCreating(true);
    try {
      await api.createSuite({
        name: createForm.name,
        model_type: createForm.model_type,
        description: createForm.description || undefined,
        category: createForm.category || undefined,
      });
      setShowCreate(false);
      setCreateForm({ name: "", model_type: "llm", description: "", category: "" });
      await loadSuites();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create suite");
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(suiteId: string, suiteName: string) {
    if (!confirm(`Delete suite "${suiteName}"? This cannot be undone.`)) return;
    try {
      await api.deleteSuite(suiteId);
      if (selectedSuite === suiteId) setSelectedSuite(null);
      await loadSuites();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete suite");
    }
  }

  const selected = suites.find((s) => s.id === selectedSuite);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-400 text-lg">Loading benchmark suites...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">Error loading benchmarks</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 mb-1">
            Benchmark Suites
          </h1>
          <p className="text-sm text-slate-400">
            Manage evaluation task suites for testing AI models across education
            tiers.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-blue-600 hover:bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors"
        >
          + New Suite
        </button>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <form
            onSubmit={handleCreate}
            className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-900 p-6 shadow-2xl"
          >
            <h2 className="text-lg font-semibold text-slate-100 mb-4">
              Create Benchmark Suite
            </h2>

            <label className="block mb-3">
              <span className="text-xs font-medium text-slate-400">Name</span>
              <input
                required
                value={createForm.name}
                onChange={(e) =>
                  setCreateForm({ ...createForm, name: e.target.value })
                }
                className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="e.g. Custom LLM Education Suite"
              />
            </label>

            <label className="block mb-3">
              <span className="text-xs font-medium text-slate-400">
                Model Type
              </span>
              <select
                value={createForm.model_type}
                onChange={(e) =>
                  setCreateForm({ ...createForm, model_type: e.target.value })
                }
                className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
              >
                <option value="llm">LLM</option>
                <option value="stt">STT</option>
                <option value="tts">TTS</option>
                <option value="vad">VAD</option>
              </select>
            </label>

            <label className="block mb-3">
              <span className="text-xs font-medium text-slate-400">
                Category
              </span>
              <input
                value={createForm.category}
                onChange={(e) =>
                  setCreateForm({ ...createForm, category: e.target.value })
                }
                className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="e.g. comprehensive, quick_scan"
              />
            </label>

            <label className="block mb-4">
              <span className="text-xs font-medium text-slate-400">
                Description
              </span>
              <textarea
                value={createForm.description}
                onChange={(e) =>
                  setCreateForm({ ...createForm, description: e.target.value })
                }
                rows={2}
                className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none resize-none"
                placeholder="Describe the purpose of this suite"
              />
            </label>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating}
                className="rounded-lg bg-blue-600 hover:bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
              >
                {creating ? "Creating..." : "Create Suite"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="flex gap-6">
        {/* Suite grid */}
        <div className={`${selectedSuite ? "w-1/2" : "w-full"} transition-all`}>
          {suites.length === 0 ? (
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-16 text-center">
              <p className="text-slate-500 text-lg mb-1">
                No suites available
              </p>
              <p className="text-slate-600 text-sm">
                Click &quot;+ New Suite&quot; to create your first benchmark
                suite.
              </p>
            </div>
          ) : (
            <div
              className={`grid gap-4 ${
                selectedSuite
                  ? "grid-cols-1"
                  : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
              }`}
            >
              {suites.map((suite) => (
                <div
                  key={suite.id}
                  onClick={() =>
                    setSelectedSuite(
                      selectedSuite === suite.id ? null : suite.id
                    )
                  }
                  className={`rounded-xl border p-5 cursor-pointer transition-colors ${
                    selectedSuite === suite.id
                      ? "border-blue-500/50 bg-blue-500/5"
                      : "border-slate-800 bg-slate-900/50 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-semibold text-slate-100 pr-2">
                      {suite.name}
                    </h3>
                    <div className="flex shrink-0 gap-1.5">
                      {suite.is_builtin && (
                        <span className="inline-flex items-center rounded-full bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 text-[10px] font-medium text-amber-400 uppercase">
                          Built-in
                        </span>
                      )}
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase ${
                          typeColors[suite.model_type] ??
                          "bg-slate-500/15 text-slate-400 border-slate-500/30"
                        }`}
                      >
                        {suite.model_type}
                      </span>
                    </div>
                  </div>

                  {suite.description && (
                    <p className="text-xs text-slate-400 mb-3 line-clamp-2">
                      {suite.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>
                      {suite.task_count} task
                      {suite.task_count !== 1 ? "s" : ""}
                    </span>
                    {suite.category && (
                      <span className="rounded bg-slate-800 px-1.5 py-0.5">
                        {suite.category}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="w-1/2 rounded-xl border border-slate-800 bg-slate-900/50 p-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">
                  {selected.name}
                </h2>
                {selected.description && (
                  <p className="text-sm text-slate-400 mt-1">
                    {selected.description}
                  </p>
                )}
              </div>
              <button
                onClick={() => setSelectedSuite(null)}
                className="text-slate-500 hover:text-slate-300 text-lg"
              >
                &times;
              </button>
            </div>

            {/* Suite metadata */}
            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="rounded-lg bg-slate-800/60 px-3 py-2">
                <div className="text-[10px] uppercase text-slate-500">Type</div>
                <div className="text-sm text-slate-200">{selected.model_type.toUpperCase()}</div>
              </div>
              <div className="rounded-lg bg-slate-800/60 px-3 py-2">
                <div className="text-[10px] uppercase text-slate-500">Tasks</div>
                <div className="text-sm text-slate-200">{selected.task_count}</div>
              </div>
              <div className="rounded-lg bg-slate-800/60 px-3 py-2">
                <div className="text-[10px] uppercase text-slate-500">Category</div>
                <div className="text-sm text-slate-200">{selected.category || "—"}</div>
              </div>
              <div className="rounded-lg bg-slate-800/60 px-3 py-2">
                <div className="text-[10px] uppercase text-slate-500">Source</div>
                <div className="text-sm text-slate-200">
                  {selected.is_builtin ? "Built-in" : "Custom"}
                </div>
              </div>
            </div>

            {/* Tasks list */}
            <h3 className="text-xs font-medium uppercase text-slate-500 mb-2">
              Tasks
            </h3>

            {loadingTasks ? (
              <p className="text-sm text-slate-500">Loading tasks...</p>
            ) : suiteTasks.length === 0 ? (
              <p className="text-sm text-slate-500">No tasks configured.</p>
            ) : (
              <div className="max-h-80 overflow-y-auto space-y-1.5">
                {suiteTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between rounded-lg bg-slate-800/40 px-3 py-2"
                  >
                    <div>
                      <div className="text-sm text-slate-200">{task.name}</div>
                      <div className="text-[10px] text-slate-500">
                        {task.task_type}
                        {task.education_tier &&
                          ` · ${task.education_tier}`}
                        {task.subject && ` · ${task.subject}`}
                      </div>
                    </div>
                    <span className="text-xs text-slate-500">
                      w={task.weight}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Actions */}
            {!selected.is_builtin && (
              <div className="mt-5 pt-4 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => handleDelete(selected.id, selected.name)}
                  className="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  Delete Suite
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
