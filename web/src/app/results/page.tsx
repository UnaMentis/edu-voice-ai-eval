"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api-client";
import type { EducationTier } from "@/types/evaluation";

const EChartsWrapper = dynamic(
  () => import("@/components/charts/EChartsWrapper"),
  { ssr: false }
);

interface GradeMatrixRow {
  model_id: string;
  model_name: string;
  model_type: string;
  parameter_count_b?: number;
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

const typeColor: Record<string, string> = {
  llm: "#3b82f6",
  stt: "#10b981",
  tts: "#a855f7",
};

type Tab = "matrix" | "scatter" | "trends";

export default function ResultsPage() {
  const [rows, setRows] = useState<GradeMatrixRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("matrix");
  const [trends, setTrends] = useState<Record<string, any[]> | null>(null);
  const [trendsLoading, setTrendsLoading] = useState(false);

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

  useEffect(() => {
    if (activeTab === "trends" && !trends) {
      setTrendsLoading(true);
      api
        .getTrends()
        .then((data) => setTrends(data.trends))
        .catch(() => setTrends({}))
        .finally(() => setTrendsLoading(false));
    }
  }, [activeTab, trends]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-400 text-lg">Loading results...</div>
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

  // Scatter data: quality (overall score) vs size (params)
  const scatterData = rows
    .filter((r) => r.overall_education_score != null)
    .map((r) => ({
      name: r.model_name,
      type: r.model_type,
      x: r.parameter_count_b ?? 0,
      y: r.overall_education_score ?? 0,
    }));

  // Trend chart series
  const trendSeries =
    trends &&
    Object.entries(trends).map(([modelId, points], i) => ({
      name: modelId.slice(0, 12),
      type: "line" as const,
      smooth: true,
      data: points.map((p: any) => [p.completed_at ?? "", p.score ?? 0]),
      lineStyle: {
        color: ["#3b82f6", "#10b981", "#a855f7", "#f59e0b", "#ef4444"][i % 5],
      },
      itemStyle: {
        color: ["#3b82f6", "#10b981", "#a855f7", "#f59e0b", "#ef4444"][i % 5],
      },
    }));

  const tabs: Array<{ key: Tab; label: string }> = [
    { key: "matrix", label: "Grade Matrix" },
    { key: "scatter", label: "Quality vs Size" },
    { key: "trends", label: "Score Trends" },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100 mb-1">Results</h1>
        <p className="text-sm text-slate-400">
          Education-tier performance analysis across all evaluated models.
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 rounded-lg bg-slate-900/50 border border-slate-800 p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-slate-700 text-slate-100"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Matrix tab */}
      {activeTab === "matrix" && (
        <>
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
                        <th key={t.key} className="text-center px-5 py-3 font-medium min-w-[120px]">
                          {t.label}
                        </th>
                      ))}
                      <th className="text-center px-5 py-3 font-medium min-w-[120px] border-l border-slate-800">
                        Overall
                      </th>
                      <th className="text-center px-5 py-3 font-medium min-w-[120px]">Max Tier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr
                        key={row.model_id}
                        className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors"
                      >
                        <td className="px-5 py-3 sticky left-0 bg-slate-950/90 backdrop-blur z-10">
                          <div className="flex items-center gap-2">
                            <span className="text-slate-200 font-medium">{row.model_name}</span>
                            <span
                              className={`inline-flex shrink-0 items-center rounded-full border px-1.5 py-0.5 text-[10px] font-medium uppercase ${
                                typeBadge[row.model_type] ?? "bg-slate-500/15 text-slate-400 border-slate-500/30"
                              }`}
                            >
                              {row.model_type}
                            </span>
                          </div>
                        </td>
                        {TIERS.map((t) => {
                          const score = row[t.key];
                          return (
                            <td key={t.key} className="px-2 py-2 text-center">
                              <div
                                className={`mx-auto rounded-lg px-3 py-2 font-mono text-sm font-semibold ${cellColor(score)}`}
                              >
                                {score != null ? score.toFixed(1) : "--"}
                              </div>
                            </td>
                          );
                        })}
                        <td className="px-2 py-2 text-center border-l border-slate-800">
                          <span className={`font-mono text-sm font-bold ${overallColor(row.overall_education_score)}`}>
                            {row.overall_education_score != null ? row.overall_education_score.toFixed(1) : "--"}
                          </span>
                        </td>
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
        </>
      )}

      {/* Scatter tab: Quality vs Size */}
      {activeTab === "scatter" && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
          <h2 className="text-lg font-semibold text-slate-100 mb-2">
            Quality vs Model Size
          </h2>
          <p className="text-xs text-slate-500 mb-4">
            Overall education score vs parameter count. Higher and further-left is better (quality at lower cost).
          </p>
          {scatterData.length === 0 ? (
            <div className="py-16 text-center text-slate-500">
              No models with both score and parameter data available.
            </div>
          ) : (
            <EChartsWrapper
              option={{
                tooltip: {
                  trigger: "item",
                  formatter: (p: any) =>
                    `<b>${p.data[2]}</b><br/>Params: ${p.data[0]}B<br/>Score: ${p.data[1]}`,
                },
                xAxis: {
                  name: "Parameters (B)",
                  nameTextStyle: { color: "#94a3b8" },
                  type: "value",
                  axisLabel: { color: "#94a3b8" },
                  splitLine: { lineStyle: { color: "#1e293b" } },
                },
                yAxis: {
                  name: "Education Score",
                  nameTextStyle: { color: "#94a3b8" },
                  type: "value",
                  min: 0,
                  max: 100,
                  axisLabel: { color: "#94a3b8" },
                  splitLine: { lineStyle: { color: "#1e293b" } },
                },
                series: [
                  {
                    type: "scatter",
                    symbolSize: 16,
                    data: scatterData.map((d) => [d.x, d.y, d.name]),
                    itemStyle: {
                      color: (params: any) => {
                        const item = scatterData[params.dataIndex];
                        return typeColor[item?.type] || "#64748b";
                      },
                    },
                    label: {
                      show: true,
                      formatter: (p: any) => p.data[2],
                      position: "top",
                      color: "#cbd5e1",
                      fontSize: 10,
                    },
                  },
                ],
              }}
              height={400}
            />
          )}
        </div>
      )}

      {/* Trends tab */}
      {activeTab === "trends" && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
          <h2 className="text-lg font-semibold text-slate-100 mb-2">Score Trends</h2>
          <p className="text-xs text-slate-500 mb-4">
            Overall score progression over time per model.
          </p>
          {trendsLoading ? (
            <div className="py-16 text-center text-slate-400">Loading trends...</div>
          ) : !trendSeries || trendSeries.length === 0 ? (
            <div className="py-16 text-center text-slate-500">
              No trend data. Complete multiple evaluation runs to see trends.
            </div>
          ) : (
            <EChartsWrapper
              option={{
                tooltip: { trigger: "axis" },
                legend: {
                  data: trendSeries.map((s) => s.name),
                  bottom: 0,
                  textStyle: { color: "#94a3b8" },
                },
                xAxis: {
                  type: "category",
                  axisLabel: { color: "#94a3b8", rotate: 30, fontSize: 10 },
                  splitLine: { show: false },
                },
                yAxis: {
                  type: "value",
                  name: "Score",
                  nameTextStyle: { color: "#94a3b8" },
                  min: 0,
                  max: 100,
                  axisLabel: { color: "#94a3b8" },
                  splitLine: { lineStyle: { color: "#1e293b" } },
                },
                series: trendSeries,
              }}
              height={400}
            />
          )}
        </div>
      )}
    </div>
  );
}
