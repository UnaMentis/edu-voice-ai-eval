"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { api } from "@/lib/api-client";
import type {
  EvalModel,
  ModelType,
  HuggingFaceSearchResult,
  DownloadStatus,
} from "@/types/evaluation";

// ── Constants ────────────────────────────────────────────────

const MODEL_TYPES: Array<{ label: string; value: string }> = [
  { label: "All", value: "all" },
  { label: "LLM", value: "llm" },
  { label: "STT", value: "stt" },
  { label: "TTS", value: "tts" },
];

const typeBadgeColors: Record<string, string> = {
  llm: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  stt: "bg-green-500/15 text-green-400 border-green-500/30",
  tts: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  vad: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  embeddings: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
};

const PIPELINE_FILTERS = [
  { label: "All", value: "" },
  { label: "Text Generation", value: "text-generation" },
  { label: "Speech Recognition", value: "automatic-speech-recognition" },
  { label: "Text-to-Speech", value: "text-to-speech" },
  { label: "Image Classification", value: "image-classification" },
];

function pipelineToModelType(pipeline?: string): ModelType {
  if (!pipeline) return "llm";
  if (pipeline.includes("speech-recognition")) return "stt";
  if (pipeline.includes("text-to-speech")) return "tts";
  return "llm";
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

// ── Download status badge ────────────────────────────────────

function DownloadBadge({
  status,
  progress,
  error,
}: {
  status?: DownloadStatus;
  progress?: number;
  error?: string;
}) {
  const s = status || "none";
  if (s === "cached")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-500/15 border border-green-500/30 px-2 py-0.5 text-xs text-green-400">
        Ready
      </span>
    );
  if (s === "downloading")
    return (
      <div className="flex items-center gap-2">
        <div className="h-1.5 w-20 rounded-full bg-slate-700 overflow-hidden">
          <div
            className="h-full rounded-full bg-blue-500 transition-all"
            style={{ width: `${Math.min(100, (progress || 0) * 100)}%` }}
          />
        </div>
        <span className="text-xs text-blue-400">
          {Math.round((progress || 0) * 100)}%
        </span>
      </div>
    );
  if (s === "failed")
    return (
      <span
        className="inline-flex items-center gap-1 rounded-full bg-red-500/15 border border-red-500/30 px-2 py-0.5 text-xs text-red-400 cursor-help"
        title={error || "Download failed"}
      >
        Failed
      </span>
    );
  return (
    <span className="inline-flex items-center rounded-full bg-slate-700/50 border border-slate-600/30 px-2 py-0.5 text-xs text-slate-500">
      Not Downloaded
    </span>
  );
}

// ── Main page component ──────────────────────────────────────

export default function ModelsPage() {
  const [tab, setTab] = useState<"my" | "discover">("my");

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Models</h1>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-slate-800">
        <button
          onClick={() => setTab("my")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "my"
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          My Models
        </button>
        <button
          onClick={() => setTab("discover")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "discover"
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Discover
        </button>
      </div>

      {tab === "my" ? <MyModelsTab /> : <DiscoverTab onSwitch={() => setTab("my")} />}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// My Models tab
// ══════════════════════════════════════════════════════════════

function MyModelsTab() {
  const [models, setModels] = useState<EvalModel[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add model form
  const [showAddForm, setShowAddForm] = useState(false);
  const [showHFImport, setShowHFImport] = useState(false);
  const [newModel, setNewModel] = useState({
    name: "",
    model_type: "llm" as ModelType,
    source_type: "huggingface",
    deployment_target: "server" as const,
  });
  const [hfRepoId, setHfRepoId] = useState("");
  const [hfModelType, setHfModelType] = useState("llm");
  const [submitting, setSubmitting] = useState(false);

  // Download polling
  const [downloadingIds, setDownloadingIds] = useState<Set<string>>(new Set());

  const fetchModels = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> =
        filter !== "all" ? { model_type: filter } : {};
      const res = await api.listModels(params);
      setModels(res.items);

      // Track which models are downloading
      const dIds = new Set<string>();
      for (const m of res.items) {
        if (m.download_status === "downloading") dIds.add(m.id);
      }
      setDownloadingIds(dIds);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load models");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  // Poll for download progress
  useEffect(() => {
    if (downloadingIds.size === 0) return;
    const timer = setInterval(fetchModels, 3000);
    return () => clearInterval(timer);
  }, [downloadingIds.size, fetchModels]);

  async function handleAddModel(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createModel(newModel);
      setShowAddForm(false);
      setNewModel({ name: "", model_type: "llm", source_type: "huggingface", deployment_target: "server" });
      fetchModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create model");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleHFImport(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.importHuggingFace({ repo_id: hfRepoId, model_type: hfModelType });
      setShowHFImport(false);
      setHfRepoId("");
      fetchModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to import from HuggingFace");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDownload(modelId: string) {
    try {
      await api.startDownload(modelId);
      setDownloadingIds((prev) => new Set(prev).add(modelId));
      fetchModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    }
  }

  async function handleCancelDownload(modelId: string) {
    try {
      await api.cancelDownload(modelId);
      fetchModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancel failed");
    }
  }

  async function handleDelete(modelId: string, name: string) {
    if (!confirm(`Delete model "${name}"?`)) return;
    try {
      await api.deleteModel(modelId);
      fetchModels();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete model");
    }
  }

  if (error && !models.length) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">Error loading models</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Action buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => { setShowHFImport(true); setShowAddForm(false); }}
          className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors"
        >
          Import from HF
        </button>
        <button
          onClick={() => { setShowAddForm(true); setShowHFImport(false); }}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 transition-colors"
        >
          Add Model
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-red-200">
            Dismiss
          </button>
        </div>
      )}

      {/* HF Import form */}
      {showHFImport && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Import from HuggingFace</h3>
          <form onSubmit={handleHFImport} className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">Repository ID</label>
              <input
                type="text"
                value={hfRepoId}
                onChange={(e) => setHfRepoId(e.target.value)}
                placeholder="e.g. openai/whisper-large-v3"
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Type</label>
              <select value={hfModelType} onChange={(e) => setHfModelType(e.target.value)} className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none">
                <option value="llm">LLM</option>
                <option value="stt">STT</option>
                <option value="tts">TTS</option>
              </select>
            </div>
            <button type="submit" disabled={submitting} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors">
              {submitting ? "Importing..." : "Import"}
            </button>
            <button type="button" onClick={() => setShowHFImport(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors">
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Add model form */}
      {showAddForm && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Add New Model</h3>
          <form onSubmit={handleAddModel} className="grid grid-cols-4 gap-3">
            <div className="col-span-2">
              <label className="block text-xs text-slate-400 mb-1">Name</label>
              <input type="text" value={newModel.name} onChange={(e) => setNewModel({ ...newModel, name: e.target.value })} placeholder="Model name" className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none" required />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Type</label>
              <select value={newModel.model_type} onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value as ModelType })} className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none">
                <option value="llm">LLM</option>
                <option value="stt">STT</option>
                <option value="tts">TTS</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Source</label>
              <select value={newModel.source_type} onChange={(e) => setNewModel({ ...newModel, source_type: e.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none">
                <option value="huggingface">HuggingFace</option>
                <option value="openai">OpenAI</option>
                <option value="local">Local</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div className="col-span-4 flex gap-2">
              <button type="submit" disabled={submitting} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors">
                {submitting ? "Creating..." : "Create Model"}
              </button>
              <button type="button" onClick={() => setShowAddForm(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter bar */}
      <div className="flex gap-2 mb-6">
        {MODEL_TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => setFilter(t.value)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              filter === t.value
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && models.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-slate-400">Loading models...</p>
        </div>
      ) : models.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-slate-500 text-lg mb-1">No models found</p>
            <p className="text-slate-600 text-sm">
              Add a model or import from HuggingFace to get started.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((model) => (
            <div
              key={model.id}
              className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-100 truncate pr-2">
                  {model.name}
                </h3>
                <span
                  className={`inline-flex shrink-0 items-center rounded-full border px-2 py-0.5 text-xs font-medium uppercase ${
                    typeBadgeColors[model.model_type] ??
                    "bg-slate-500/15 text-slate-400 border-slate-500/30"
                  }`}
                >
                  {model.model_type}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-400">
                {model.parameter_count_b != null && (
                  <p><span className="text-slate-500">Params:</span> {model.parameter_count_b}B</p>
                )}
                <p><span className="text-slate-500">Source:</span> {model.source_type}</p>
                <p><span className="text-slate-500">Deploy:</span> {model.deployment_target}</p>
                {model.model_family && (
                  <p><span className="text-slate-500">Family:</span> {model.model_family}</p>
                )}
              </div>

              {/* Download status */}
              <div className="mt-3">
                <DownloadBadge
                  status={model.download_status}
                  progress={model.download_progress}
                  error={model.download_error}
                />
              </div>

              {model.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {model.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-500">
                      {tag}
                    </span>
                  ))}
                  {model.tags.length > 3 && (
                    <span className="text-xs text-slate-600">+{model.tags.length - 3}</span>
                  )}
                </div>
              )}

              {/* Action buttons */}
              <div className="mt-4 flex gap-2">
                {(!model.download_status || model.download_status === "none") && model.source_type === "huggingface" && (
                  <button onClick={() => handleDownload(model.id)} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500 transition-colors">
                    Download
                  </button>
                )}
                {model.download_status === "downloading" && (
                  <button onClick={() => handleCancelDownload(model.id)} className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/20 transition-colors">
                    Cancel
                  </button>
                )}
                {model.download_status === "failed" && (
                  <button onClick={() => handleDownload(model.id)} className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs text-white hover:bg-amber-500 transition-colors">
                    Retry
                  </button>
                )}
                <button
                  onClick={() => handleDelete(model.id, model.name)}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-500 hover:text-red-400 hover:border-red-500/30 transition-colors ml-auto"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

// ══════════════════════════════════════════════════════════════
// Discover tab
// ══════════════════════════════════════════════════════════════

function DiscoverTab({ onSwitch }: { onSwitch: () => void }) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [task, setTask] = useState("");
  const [sort, setSort] = useState("downloads");
  const [results, setResults] = useState<HuggingFaceSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Debounce search query
  useEffect(() => {
    debounceRef.current = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(debounceRef.current);
  }, [query]);

  // Search when debounced query, task, or sort changes
  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([]);
      return;
    }

    let cancelled = false;
    async function search() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.searchHuggingFace({
          q: debouncedQuery,
          task: task || undefined,
          sort,
          limit: 20,
        });
        if (!cancelled) setResults(res.items);
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Search failed");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    search();
    return () => { cancelled = true; };
  }, [debouncedQuery, task, sort]);

  async function handleImport(result: HuggingFaceSearchResult, andDownload: boolean) {
    setImporting(result.repo_id);
    try {
      const model = await api.importHuggingFace({
        repo_id: result.repo_id,
        model_type: pipelineToModelType(result.pipeline_tag),
      });
      if (andDownload && model.id) {
        await api.startDownload(model.id);
      }
      onSwitch(); // go to My Models
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(null);
    }
  }

  return (
    <>
      {/* Search bar */}
      <div className="flex gap-3 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search HuggingFace models..."
          className="flex-1 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          autoFocus
        />
        <select
          value={task}
          onChange={(e) => setTask(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
        >
          {PIPELINE_FILTERS.map((f) => (
            <option key={f.value} value={f.value}>{f.label}</option>
          ))}
        </select>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
        >
          <option value="downloads">Most Downloads</option>
          <option value="likes">Most Likes</option>
          <option value="lastModified">Recently Updated</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-red-200">Dismiss</button>
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-slate-400">Searching HuggingFace...</p>
        </div>
      ) : !debouncedQuery.trim() ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-slate-500 text-lg mb-1">Search for models</p>
            <p className="text-slate-600 text-sm">
              Type a query above to search HuggingFace Hub
            </p>
          </div>
        </div>
      ) : results.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-slate-500">No results found for &ldquo;{debouncedQuery}&rdquo;</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((r) => (
            <div
              key={r.repo_id}
              className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="min-w-0">
                  <h3 className="text-sm font-semibold text-slate-100 truncate">
                    {r.name}
                  </h3>
                  {r.author && (
                    <p className="text-xs text-slate-500 truncate">{r.author}</p>
                  )}
                </div>
                {r.pipeline_tag && (
                  <span className="inline-flex shrink-0 items-center rounded-full border border-slate-600/30 bg-slate-700/50 px-2 py-0.5 text-xs text-slate-400 ml-2">
                    {r.pipeline_tag}
                  </span>
                )}
              </div>

              <div className="flex gap-4 text-xs text-slate-400 mb-3">
                <span title="Downloads">{formatNumber(r.downloads)} downloads</span>
                <span title="Likes">{formatNumber(r.likes)} likes</span>
                {r.parameter_count_b != null && (
                  <span>{r.parameter_count_b}B params</span>
                )}
              </div>

              {r.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {r.tags.slice(0, 4).map((tag) => (
                    <span key={tag} className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-500">
                      {tag}
                    </span>
                  ))}
                  {r.tags.length > 4 && (
                    <span className="text-xs text-slate-600">+{r.tags.length - 4}</span>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => handleImport(r, true)}
                  disabled={importing === r.repo_id}
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
                >
                  {importing === r.repo_id ? "Importing..." : "Import & Download"}
                </button>
                <button
                  onClick={() => handleImport(r, false)}
                  disabled={importing === r.repo_id}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 disabled:opacity-50 transition-colors"
                >
                  Import Only
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
