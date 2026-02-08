"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { EvalModel, EvalRun, BenchmarkSuite } from "@/types/evaluation";

export default function OverviewPage() {
  const [models, setModels] = useState<EvalModel[]>([]);
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [suites, setSuites] = useState<BenchmarkSuite[]>([]);
  const [totalModels, setTotalModels] = useState(0);
  const [totalRuns, setTotalRuns] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [modelsRes, runsRes, suitesRes] = await Promise.all([
          api.listModels(),
          api.listRuns({ limit: "10" }),
          api.listSuites(),
        ]);
        setModels(modelsRes.items);
        setTotalModels(modelsRes.total);
        setRuns(runsRes.items);
        setTotalRuns(runsRes.total);
        setSuites(suitesRes.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const avgScore =
    runs.filter((r) => r.overall_score != null).length > 0
      ? (
          runs
            .filter((r) => r.overall_score != null)
            .reduce((sum, r) => sum + (r.overall_score ?? 0), 0) /
          runs.filter((r) => r.overall_score != null).length
        ).toFixed(1)
      : "--";

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-400 text-lg">Loading overview...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">Error loading data</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: "Total Models",
      value: totalModels,
      color: "text-blue-400",
      bg: "bg-blue-500/10 border-blue-500/20",
    },
    {
      label: "Total Runs",
      value: totalRuns,
      color: "text-green-400",
      bg: "bg-green-500/10 border-green-500/20",
    },
    {
      label: "Avg Score",
      value: avgScore,
      color: "text-purple-400",
      bg: "bg-purple-500/10 border-purple-500/20",
    },
    {
      label: "Suites Available",
      value: suites.length,
      color: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">Overview</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className={`rounded-xl border p-5 ${stat.bg}`}
          >
            <p className="text-sm text-slate-400 mb-1">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Recent runs */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-slate-100">
            Recent Runs
          </h2>
        </div>

        {runs.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-slate-500 text-lg mb-1">No data yet</p>
            <p className="text-slate-600 text-sm">
              Start an evaluation run to see results here.
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
                      <StatusBadge status={run.status} />
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
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed: "bg-green-500/15 text-green-400 border-green-500/30",
    running: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    pending: "bg-slate-500/15 text-slate-400 border-slate-500/30",
    queued: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    failed: "bg-red-500/15 text-red-400 border-red-500/30",
    cancelled: "bg-slate-500/15 text-slate-500 border-slate-500/30",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${
        styles[status] ?? styles.pending
      }`}
    >
      {status}
    </span>
  );
}
