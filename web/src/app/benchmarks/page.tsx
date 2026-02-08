"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { BenchmarkSuite } from "@/types/evaluation";

const typeColors: Record<string, string> = {
  llm: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  stt: "bg-green-500/15 text-green-400 border-green-500/30",
  tts: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  vad: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  mixed: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
};

export default function BenchmarksPage() {
  const [suites, setSuites] = useState<BenchmarkSuite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.listSuites();
        setSuites(res.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load suites");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

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
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100 mb-1">
          Benchmark Suites
        </h1>
        <p className="text-sm text-slate-400">
          Evaluation task suites for testing AI models across education tiers.
        </p>
      </div>

      {suites.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-16 text-center">
          <p className="text-slate-500 text-lg mb-1">No suites available</p>
          <p className="text-slate-600 text-sm">
            Benchmark suites will appear here once configured.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {suites.map((suite) => (
            <div
              key={suite.id}
              className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-slate-700 transition-colors"
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
                  {suite.task_count} task{suite.task_count !== 1 ? "s" : ""}
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
  );
}
