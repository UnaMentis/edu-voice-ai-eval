"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface SharedReport {
  id: string;
  token: string;
  report_type: string;
  report_config: Record<string, any>;
  expires_at?: string;
  view_count?: number;
  created_at?: string;
}

export default function SharedReportPage() {
  const params = useParams();
  const token = params.token as string;
  const [report, setReport] = useState<SharedReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`/api/eval/share/${token}`);
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || `Error ${res.status}`);
        }
        setReport(await res.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      } finally {
        setLoading(false);
      }
    }
    if (token) load();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-slate-400 text-lg">Loading shared report...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-xl mb-2">Report Unavailable</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!report) return null;

  const config = report.report_config || {};

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Header */}
      <div className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-slate-100">
              Shared Evaluation Report
            </h1>
            <p className="text-xs text-slate-500">
              {report.report_type} &middot; Shared{" "}
              {report.created_at
                ? new Date(report.created_at).toLocaleDateString()
                : ""}
            </p>
          </div>
          <span className="text-xs text-slate-600">
            {report.view_count ?? 0} views
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        {report.report_type === "run" && config.run_id && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">
              Evaluation Run
            </h2>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-slate-500">Run ID</dt>
                <dd className="font-mono text-slate-300">{config.run_id}</dd>
              </div>
              {config.model_name && (
                <div>
                  <dt className="text-slate-500">Model</dt>
                  <dd className="text-slate-300">{config.model_name}</dd>
                </div>
              )}
              {config.suite_name && (
                <div>
                  <dt className="text-slate-500">Suite</dt>
                  <dd className="text-slate-300">{config.suite_name}</dd>
                </div>
              )}
              {config.overall_score != null && (
                <div>
                  <dt className="text-slate-500">Overall Score</dt>
                  <dd className="text-2xl font-bold text-green-400">
                    {config.overall_score.toFixed(1)}
                  </dd>
                </div>
              )}
            </dl>

            {config.grade_level && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-slate-400 mb-2">
                  Grade Level Assessment
                </h3>
                <p className="text-slate-300">
                  Max Passing Tier:{" "}
                  <span className="font-semibold text-green-400">
                    {config.grade_level.max_passing_tier || "None"}
                  </span>
                </p>
              </div>
            )}
          </div>
        )}

        {report.report_type === "comparison" && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">
              Model Comparison
            </h2>
            {config.models && Array.isArray(config.models) ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="text-left px-4 py-2">Model</th>
                      <th className="text-center px-4 py-2">Score</th>
                      <th className="text-center px-4 py-2">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {config.models.map((m: any, i: number) => (
                      <tr key={i} className="border-b border-slate-800/50">
                        <td className="px-4 py-2 text-slate-200">{m.name || m.model_name}</td>
                        <td className="px-4 py-2 text-center font-mono text-slate-300">
                          {m.score != null ? m.score.toFixed(1) : "--"}
                        </td>
                        <td className="px-4 py-2 text-center text-slate-400 uppercase text-xs">
                          {m.model_type || "--"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-500">No comparison data available.</p>
            )}
          </div>
        )}

        {report.report_type === "model_card" && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">
              Model Card
            </h2>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              {config.model_name && (
                <div>
                  <dt className="text-slate-500">Model</dt>
                  <dd className="text-slate-200 font-medium">{config.model_name}</dd>
                </div>
              )}
              {config.model_type && (
                <div>
                  <dt className="text-slate-500">Type</dt>
                  <dd className="text-slate-300 uppercase">{config.model_type}</dd>
                </div>
              )}
              {config.parameter_count_b != null && (
                <div>
                  <dt className="text-slate-500">Parameters</dt>
                  <dd className="text-slate-300">{config.parameter_count_b}B</dd>
                </div>
              )}
              {config.max_passing_tier && (
                <div>
                  <dt className="text-slate-500">Max Education Tier</dt>
                  <dd className="text-green-400 font-medium">{config.max_passing_tier}</dd>
                </div>
              )}
            </dl>
          </div>
        )}

        {/* Expiry notice */}
        {report.expires_at && (
          <p className="mt-6 text-xs text-slate-600 text-center">
            This report expires on{" "}
            {new Date(report.expires_at).toLocaleDateString()}.
          </p>
        )}
      </div>
    </div>
  );
}
