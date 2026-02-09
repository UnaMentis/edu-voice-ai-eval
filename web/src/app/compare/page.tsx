"use client";

import { useEffect, useState, useMemo } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api-client";
import type { EvalModel } from "@/types/evaluation";

const EChartsWrapper = dynamic(
  () => import("@/components/charts/EChartsWrapper"),
  { ssr: false }
);

interface ComparisonEntry {
  model: Record<string, any>;
  latest_run: Record<string, any> | null;
  results: Array<Record<string, any>>;
}

export default function ComparePage() {
  const [allModels, setAllModels] = useState<EvalModel[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparison, setComparison] = useState<{
    comparisons: ComparisonEntry[];
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
      if (prev.length >= 5) return prev;
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

  // Extract tier-level scores for radar chart
  const radarData = useMemo(() => {
    if (!comparison?.comparisons) return null;

    const dimensions = ["elementary", "high_school", "undergraduate", "graduate"];
    const dimLabels = ["Elementary", "High School", "Undergraduate", "Graduate"];

    const series: Array<{ name: string; values: number[] }> = [];

    for (const entry of comparison.comparisons) {
      const tierScores: Record<string, number[]> = {};
      for (const d of dimensions) tierScores[d] = [];

      for (const r of entry.results) {
        const tier = r.education_tier;
        if (tier && tier in tierScores && r.score != null) {
          tierScores[tier].push(r.score);
        }
      }

      const values = dimensions.map((d) => {
        const scores = tierScores[d];
        return scores.length ? Math.round((scores.reduce((a: number, b: number) => a + b, 0) / scores.length) * 10) / 10 : 0;
      });

      series.push({
        name: entry.model?.name || "Unknown",
        values,
      });
    }

    if (series.every((s) => s.values.every((v) => v === 0))) return null;

    return { dimensions: dimLabels, series };
  }, [comparison]);

  // Build comparison table rows
  const tableRows = useMemo(() => {
    if (!comparison?.comparisons?.length) return [];

    const rows: Array<{ label: string; values: Array<{ value: number | null; isBest: boolean; delta?: number }> }> = [];

    // Overall score
    const overallScores = comparison.comparisons.map(
      (e) => e.latest_run?.overall_score ?? null
    );
    const maxOverall = Math.max(...overallScores.filter((v): v is number => v != null));
    rows.push({
      label: "Overall Score",
      values: overallScores.map((v) => ({ value: v, isBest: v === maxOverall && v != null && v > 0 })),
    });

    // Parameters
    const params = comparison.comparisons.map((e) => e.model?.parameter_count_b ?? null);
    rows.push({
      label: "Parameters (B)",
      values: params.map((v) => ({ value: v, isBest: false })),
    });

    // Task count
    const taskCounts = comparison.comparisons.map((e) => e.results?.length ?? null);
    rows.push({
      label: "Tasks Evaluated",
      values: taskCounts.map((v) => ({ value: v, isBest: false })),
    });

    // Per-tier scores
    const tiers = ["elementary", "high_school", "undergraduate", "graduate"];
    const tierLabels: Record<string, string> = {
      elementary: "Elementary Score",
      high_school: "High School Score",
      undergraduate: "Undergraduate Score",
      graduate: "Graduate Score",
    };

    for (const tier of tiers) {
      const tierScores = comparison.comparisons.map((entry) => {
        const tierResults = entry.results.filter(
          (r: any) => r.education_tier === tier && r.score != null
        );
        if (!tierResults.length) return null;
        return Math.round(
          (tierResults.reduce((sum: number, r: any) => sum + r.score, 0) / tierResults.length) * 10
        ) / 10;
      });
      const maxTier = Math.max(...tierScores.filter((v): v is number => v != null));

      if (tierScores.some((v) => v != null)) {
        rows.push({
          label: tierLabels[tier],
          values: tierScores.map((v) => ({ value: v, isBest: v === maxTier && v != null && v > 0 })),
        });
      }
    }

    // Delta from reference (first reference model)
    const refIdx = comparison.comparisons.findIndex((e) => e.model?.is_reference);
    if (refIdx >= 0 && overallScores[refIdx] != null) {
      const refScore = overallScores[refIdx]!;
      rows.push({
        label: "Delta from Reference",
        values: overallScores.map((v, i) => ({
          value: v != null ? Math.round((v - refScore) * 10) / 10 : null,
          isBest: false,
          delta: v != null ? v - refScore : undefined,
        })),
      });
    }

    return rows;
  }, [comparison]);

  const modelColors = ["#3b82f6", "#10b981", "#a855f7", "#f59e0b", "#ef4444"];

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">Compare Models</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-red-200">
            Dismiss
          </button>
        </div>
      )}

      {/* Model selection */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-200">Select Models (2-5)</h2>
          <span className="text-xs text-slate-500">{selectedIds.length} selected</span>
        </div>

        {loading ? (
          <p className="text-slate-400 text-sm">Loading models...</p>
        ) : allModels.length === 0 ? (
          <p className="text-slate-500 text-sm">No models available. Add models first.</p>
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
                    <span className="ml-1.5 text-xs uppercase opacity-60">{model.model_type}</span>
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

      {comparison && comparison.comparisons.length > 0 && (
        <>
          {/* Radar chart */}
          {radarData && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 mb-6">
              <h2 className="text-lg font-semibold text-slate-100 mb-4">
                Education Tier Radar
              </h2>
              <EChartsWrapper
                option={{
                  tooltip: { trigger: "item" },
                  legend: {
                    data: radarData.series.map((s) => s.name),
                    bottom: 0,
                    textStyle: { color: "#94a3b8" },
                  },
                  radar: {
                    indicator: radarData.dimensions.map((d) => ({
                      name: d,
                      max: 100,
                    })),
                    shape: "polygon",
                    axisName: { color: "#94a3b8", fontSize: 12 },
                    splitArea: { areaStyle: { color: ["rgba(15,23,42,0.6)", "rgba(30,41,59,0.4)"] } },
                    splitLine: { lineStyle: { color: "#334155" } },
                    axisLine: { lineStyle: { color: "#334155" } },
                  },
                  series: [
                    {
                      type: "radar",
                      data: radarData.series.map((s, i) => ({
                        value: s.values,
                        name: s.name,
                        lineStyle: { color: modelColors[i % modelColors.length], width: 2 },
                        areaStyle: { color: modelColors[i % modelColors.length], opacity: 0.1 },
                        itemStyle: { color: modelColors[i % modelColors.length] },
                      })),
                    },
                  ],
                }}
                height={400}
              />
            </div>
          )}

          {/* Comparison table with delta highlighting */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden mb-6">
            <div className="px-5 py-4 border-b border-slate-800">
              <h2 className="text-lg font-semibold text-slate-100">Comparison Table</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="text-left px-5 py-3 font-medium">Metric</th>
                    {comparison.comparisons.map((entry, i) => (
                      <th key={entry.model?.id || i} className="text-center px-5 py-3 font-medium">
                        <span style={{ color: modelColors[i % modelColors.length] }}>
                          {entry.model?.name || "Unknown"}
                        </span>
                        {entry.model?.is_reference && (
                          <span className="ml-1 text-[10px] text-yellow-400">(ref)</span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableRows.map((row) => (
                    <tr key={row.label} className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors">
                      <td className="px-5 py-3 text-slate-300 font-medium">{row.label}</td>
                      {row.values.map((cell, i) => (
                        <td key={i} className="px-5 py-3 text-center font-mono">
                          <span
                            className={
                              cell.isBest
                                ? "text-green-400 font-bold"
                                : cell.delta !== undefined
                                  ? cell.delta > 0
                                    ? "text-green-400"
                                    : cell.delta < 0
                                      ? "text-red-400"
                                      : "text-slate-400"
                                  : "text-slate-300"
                            }
                          >
                            {cell.value != null
                              ? `${cell.delta !== undefined && cell.value > 0 ? "+" : ""}${cell.value.toFixed(1)}`
                              : "--"}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {comparison && comparison.comparisons.length === 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-12 text-center">
          <p className="text-slate-500 text-lg mb-1">No comparison data available</p>
          <p className="text-slate-600 text-sm">
            The selected models may not have completed evaluation runs yet.
          </p>
        </div>
      )}

      {!comparison && selectedIds.length === 0 && !loading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-12 text-center">
          <p className="text-slate-500 text-lg mb-1">Select models to compare</p>
          <p className="text-slate-600 text-sm">
            Choose 2 to 5 models above, then click &quot;Compare Selected&quot; to see
            side-by-side results with radar chart.
          </p>
        </div>
      )}
    </div>
  );
}
