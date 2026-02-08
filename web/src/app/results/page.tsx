"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import type { EducationTier } from "@/types/evaluation";

/** Shape returned by api.getGradeMatrix() */
interface GradeMatrixRow {
  model_id: string;
  model_name: string;
  model_type: string;
  elementary?: number;
  highschool?: number;
  undergrad?: number;
  grad?: number;
  overall_education_score?: number;
  max_passing_tier?: string;
}

const TIERS: Array<{ key: EducationTier; label: string }> = [
  { key: "elementary", label: "Elementary" },
  { key: "highschool", label: "High School" },
  { key: "undergrad", label: "Undergraduate" },
  { key: "grad", label: "Graduate" },
];

const PASS_THRESHOLD = 70;

function cellColor(score: number | undefined | null): string {
  if (score == null) return "bg-slate-800 text-slate-600";
  if (score >= PASS_THRESHOLD) return "bg-green-600/25 text-green-300";
  return "bg-red-600/25 text-red-300";
}

function overallColor(score: number | undefined | null): string {
  if (score == null) return "text-slate-600";
  if (score >= 80) return "text-green-400";
  if (score >= PASS_THRESHOLD) return "text-yellow-400";
  return "text-red-400";
}

const typeBadge: Record<string, string> = {
  llm: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  stt: "bg-green-500/15 text-green-400 border-green-500/30",
  tts: "bg-purple-500/15 text-purple-400 border-purple-500/30",
};

export default function ResultsPage() {
  const [rows, setRows] = useState<GradeMatrixRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getGradeMatrix();
        setRows((data as any).matrix ?? (data as any).rows ?? []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load grade matrix"
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-400 text-lg">
          Loading grade-level matrix...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">Error loading results</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100 mb-1">
          Grade-Level Results Matrix
        </h1>
        <p className="text-sm text-slate-400">
          Education-tier performance heatmap. Green indicates a passing score
          (&ge;{PASS_THRESHOLD}), red indicates failing, gray means no data.
        </p>
      </div>

      {/* Legend */}
      <div className="flex gap-4 mb-6 text-xs text-slate-400">
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded bg-green-600/40" />
          Pass (&ge;{PASS_THRESHOLD})
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded bg-red-600/40" />
          Fail (&lt;{PASS_THRESHOLD})
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded bg-slate-800" />
          No data
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-16 text-center">
          <p className="text-slate-500 text-lg mb-1">No data yet</p>
          <p className="text-slate-600 text-sm">
            Run evaluations with education-tier tasks to populate this matrix.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="text-left px-5 py-3 font-medium sticky left-0 bg-slate-900/90 backdrop-blur z-10">
                    Model
                  </th>
                  {TIERS.map((t) => (
                    <th
                      key={t.key}
                      className="text-center px-5 py-3 font-medium min-w-[120px]"
                    >
                      {t.label}
                    </th>
                  ))}
                  <th className="text-center px-5 py-3 font-medium min-w-[120px] border-l border-slate-800">
                    Overall
                  </th>
                  <th className="text-center px-5 py-3 font-medium min-w-[120px]">
                    Max Tier
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.model_id}
                    className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors"
                  >
                    {/* Model name + type */}
                    <td className="px-5 py-3 sticky left-0 bg-slate-950/90 backdrop-blur z-10">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-200 font-medium">
                          {row.model_name}
                        </span>
                        <span
                          className={`inline-flex shrink-0 items-center rounded-full border px-1.5 py-0.5 text-[10px] font-medium uppercase ${
                            typeBadge[row.model_type] ??
                            "bg-slate-500/15 text-slate-400 border-slate-500/30"
                          }`}
                        >
                          {row.model_type}
                        </span>
                      </div>
                    </td>

                    {/* Tier score cells */}
                    {TIERS.map((t) => {
                      const score = row[t.key];
                      return (
                        <td key={t.key} className="px-2 py-2 text-center">
                          <div
                            className={`mx-auto rounded-lg px-3 py-2 font-mono text-sm font-semibold ${cellColor(
                              score
                            )}`}
                          >
                            {score != null ? score.toFixed(1) : "--"}
                          </div>
                        </td>
                      );
                    })}

                    {/* Overall score */}
                    <td className="px-2 py-2 text-center border-l border-slate-800">
                      <span
                        className={`font-mono text-sm font-bold ${overallColor(
                          row.overall_education_score
                        )}`}
                      >
                        {row.overall_education_score != null
                          ? row.overall_education_score.toFixed(1)
                          : "--"}
                      </span>
                    </td>

                    {/* Max passing tier */}
                    <td className="px-5 py-3 text-center">
                      {row.max_passing_tier ? (
                        <span className="inline-flex items-center rounded-full bg-green-500/10 border border-green-500/20 px-2.5 py-0.5 text-xs font-medium text-green-400">
                          {row.max_passing_tier}
                        </span>
                      ) : (
                        <span className="text-slate-600 text-xs">--</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
