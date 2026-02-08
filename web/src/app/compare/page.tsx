"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { EvalModel } from "@/types/evaluation";

export default function ComparePage() {
  const [allModels, setAllModels] = useState<EvalModel[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparison, setComparison] = useState<{
    comparisons: Array<Record<string, any>>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.listModels();
        setAllModels(res.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load models");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function toggleModel(id: string) {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 5) return prev; // max 5
      return [...prev, id];
    });
    setComparison(null);
  }

  async function handleCompare() {
    if (selectedIds.length < 2) return;
    setComparing(true);
    setError(null);
    try {
      const res = await api.compareModels(selectedIds);
      setComparison(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed");
    } finally {
      setComparing(false);
    }
  }

  const selectedModels = allModels.filter((m) => selectedIds.includes(m.id));

  // Build metric keys from comparison data
  const metricKeys: string[] = [];
  if (comparison?.comparisons) {
    const keySet = new Set<string>();
    for (const entry of comparison.comparisons) {
      for (const key of Object.keys(entry)) {
        if (key !== "model_id" && key !== "model_name") keySet.add(key);
      }
    }
    metricKeys.push(...keySet);
  }

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">
        Compare Models
      </h1>

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

      {/* Model selection */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-200">
            Select Models (2-5)
          </h2>
          <span className="text-xs text-slate-500">
            {selectedIds.length} selected
          </span>
        </div>

        {loading ? (
          <p className="text-slate-400 text-sm">Loading models...</p>
        ) : allModels.length === 0 ? (
          <p className="text-slate-500 text-sm">
            No models available. Add models first.
          </p>
        ) : (
          <>
            <div className="flex flex-wrap gap-2 mb-4">
              {allModels.map((model) => {
                const isSelected = selectedIds.includes(model.id);
                return (
                  <button
                    key={model.id}
                    onClick={() => toggleModel(model.id)}
                    className={`rounded-lg border px-3 py-2 text-sm transition-colors ${
                      isSelected
                        ? "border-blue-500 bg-blue-600/20 text-blue-300"
                        : "border-slate-700 bg-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-600"
                    }`}
                  >
                    <span className="font-medium">{model.name}</span>
                    <span className="ml-1.5 text-xs uppercase opacity-60">
                      {model.model_type}
                    </span>
                  </button>
                );
              })}
            </div>

            <button
              onClick={handleCompare}
              disabled={selectedIds.length < 2 || comparing}
              className="rounded-lg bg-blue-600 px-5 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {comparing ? "Comparing..." : "Compare Selected"}
            </button>
          </>
        )}
      </div>

      {/* Comparison results */}
      {comparison && comparison.comparisons.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800">
            <h2 className="text-lg font-semibold text-slate-100">
              Comparison Results
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="text-left px-5 py-3 font-medium">Metric</th>
                  {comparison.comparisons.map((entry) => (
                    <th
                      key={entry.model_id ?? entry.model_name}
                      className="text-center px-5 py-3 font-medium"
                    >
                      {entry.model_name ?? entry.model_id}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metricKeys.map((key) => {
                  const values = comparison.comparisons.map(
                    (e) => e[key] as number | undefined
                  );
                  const max = Math.max(
                    ...values.filter((v): v is number => v != null)
                  );

                  return (
                    <tr
                      key={key}
                      className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors"
                    >
                      <td className="px-5 py-3 text-slate-300 font-medium capitalize">
                        {key.replace(/_/g, " ")}
                      </td>
                      {comparison.comparisons.map((entry) => {
                        const val = entry[key];
                        const isMax =
                          typeof val === "number" && val === max && max > 0;
                        return (
                          <td
                            key={entry.model_id ?? entry.model_name}
                            className="px-5 py-3 text-center font-mono"
                          >
                            <span
                              className={
                                isMax
                                  ? "text-green-400 font-bold"
                                  : "text-slate-300"
                              }
                            >
                              {typeof val === "number" ? val.toFixed(1) : "--"}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty comparison state */}
      {comparison && comparison.comparisons.length === 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-12 text-center">
          <p className="text-slate-500 text-lg mb-1">
            No comparison data available
          </p>
          <p className="text-slate-600 text-sm">
            The selected models may not have completed evaluation runs yet.
          </p>
        </div>
      )}

      {/* No selection yet */}
      {!comparison && selectedIds.length === 0 && !loading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-12 text-center">
          <p className="text-slate-500 text-lg mb-1">Select models to compare</p>
          <p className="text-slate-600 text-sm">
            Choose 2 to 5 models above, then click &quot;Compare Selected&quot;
            to see side-by-side results.
          </p>
        </div>
      )}
    </div>
  );
}
