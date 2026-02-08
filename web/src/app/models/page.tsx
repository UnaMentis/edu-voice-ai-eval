"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { EvalModel, ModelType } from "@/types/evaluation";

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

export default function ModelsPage() {
  const [models, setModels] = useState<EvalModel[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add model form state
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

  useEffect(() => {
    fetchModels();
  }, [filter]);

  async function fetchModels() {
    setLoading(true);
    try {
      const params: Record<string, string> =
        filter !== "all" ? { model_type: filter } : {};
      const res = await api.listModels(params);
      setModels(res.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load models");
    } finally {
      setLoading(false);
    }
  }

  async function handleAddModel(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createModel(newModel);
      setShowAddForm(false);
      setNewModel({
        name: "",
        model_type: "llm",
        source_type: "huggingface",
        deployment_target: "server",
      });
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
      await api.importHuggingFace({
        repo_id: hfRepoId,
        model_type: hfModelType,
      });
      setShowHFImport(false);
      setHfRepoId("");
      fetchModels();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to import from HuggingFace"
      );
    } finally {
      setSubmitting(false);
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
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Models</h1>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setShowHFImport(true);
              setShowAddForm(false);
            }}
            className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors"
          >
            Import from HF
          </button>
          <button
            onClick={() => {
              setShowAddForm(true);
              setShowHFImport(false);
            }}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 transition-colors"
          >
            Add Model
          </button>
        </div>
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

      {/* HF Import form */}
      {showHFImport && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">
            Import from HuggingFace
          </h3>
          <form onSubmit={handleHFImport} className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1">
                Repository ID
              </label>
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
              <select
                value={hfModelType}
                onChange={(e) => setHfModelType(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="llm">LLM</option>
                <option value="stt">STT</option>
                <option value="tts">TTS</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
            >
              {submitting ? "Importing..." : "Import"}
            </button>
            <button
              type="button"
              onClick={() => setShowHFImport(false)}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Add model form */}
      {showAddForm && (
        <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">
            Add New Model
          </h3>
          <form onSubmit={handleAddModel} className="grid grid-cols-4 gap-3">
            <div className="col-span-2">
              <label className="block text-xs text-slate-400 mb-1">Name</label>
              <input
                type="text"
                value={newModel.name}
                onChange={(e) =>
                  setNewModel({ ...newModel, name: e.target.value })
                }
                placeholder="Model name"
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Type</label>
              <select
                value={newModel.model_type}
                onChange={(e) =>
                  setNewModel({
                    ...newModel,
                    model_type: e.target.value as ModelType,
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="llm">LLM</option>
                <option value="stt">STT</option>
                <option value="tts">TTS</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Source
              </label>
              <select
                value={newModel.source_type}
                onChange={(e) =>
                  setNewModel({ ...newModel, source_type: e.target.value })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="huggingface">HuggingFace</option>
                <option value="openai">OpenAI</option>
                <option value="local">Local</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div className="col-span-4 flex gap-2">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
              >
                {submitting ? "Creating..." : "Create Model"}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
              >
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
      {loading ? (
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
        /* Model cards grid */
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
                  <p>
                    <span className="text-slate-500">Params:</span>{" "}
                    {model.parameter_count_b}B
                  </p>
                )}
                <p>
                  <span className="text-slate-500">Source:</span>{" "}
                  {model.source_type}
                </p>
                <p>
                  <span className="text-slate-500">Deploy:</span>{" "}
                  {model.deployment_target}
                </p>
                {model.model_family && (
                  <p>
                    <span className="text-slate-500">Family:</span>{" "}
                    {model.model_family}
                  </p>
                )}
              </div>

              {model.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {model.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-500"
                    >
                      {tag}
                    </span>
                  ))}
                  {model.tags.length > 3 && (
                    <span className="text-xs text-slate-600">
                      +{model.tags.length - 3}
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
