"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api-client";

interface SharedLink {
  id: string;
  url: string;
  label: string;
  created_at: string;
}

export default function ReportsPage() {
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [exportResult, setExportResult] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sharedLinks, setSharedLinks] = useState<SharedLink[]>([]);
  const [linksLoading, setLinksLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadSharedLinks();
  }, []);

  async function loadSharedLinks() {
    setLinksLoading(true);
    try {
      const links = await api.listSharedLinks();
      setSharedLinks(Array.isArray(links) ? links : []);
    } catch {
      // Shared links may not be available — that's okay
      setSharedLinks([]);
    } finally {
      setLinksLoading(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    setError(null);
    setExportResult(null);
    try {
      const data = await api.exportData({});
      // Trigger download
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `eval-export-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setExportResult("Export downloaded successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setImporting(true);
    setError(null);
    setImportResult(null);

    try {
      const text = await file.text();
      const data = JSON.parse(text);
      await api.importData(data);
      setImportResult(`Imported data from "${file.name}" successfully.`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Import failed. Check file format."
      );
    } finally {
      setImporting(false);
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDeleteLink(id: string) {
    try {
      await api.deleteSharedLink(id);
      setSharedLinks((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete shared link"
      );
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">Reports</h1>

      {/* Error / success banners */}
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
      {exportResult && (
        <div className="mb-4 rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm text-green-400">
          {exportResult}
        </div>
      )}
      {importResult && (
        <div className="mb-4 rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm text-green-400">
          {importResult}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Export card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="text-lg font-semibold text-slate-100 mb-2">
            Export Data
          </h2>
          <p className="text-sm text-slate-400 mb-4">
            Download all models, runs, and results as a JSON file for backup or
            analysis.
          </p>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm text-white hover:bg-blue-500 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            {exporting ? "Exporting..." : "Export JSON"}
          </button>
        </div>

        {/* Import card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="text-lg font-semibold text-slate-100 mb-2">
            Import Data
          </h2>
          <p className="text-sm text-slate-400 mb-4">
            Upload a previously exported JSON file to restore or merge
            evaluation data.
          </p>
          <label
            className={`rounded-lg border-2 border-dashed px-5 py-4 flex flex-col items-center gap-2 cursor-pointer transition-colors ${
              importing
                ? "border-slate-700 bg-slate-800/50"
                : "border-slate-700 hover:border-blue-500/50 hover:bg-slate-800/30"
            }`}
          >
            <svg
              className="w-6 h-6 text-slate-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <span className="text-sm text-slate-400">
              {importing ? "Importing..." : "Click to upload JSON file"}
            </span>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleImport}
              disabled={importing}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Shared links */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-slate-100">
            Shared Links
          </h2>
        </div>

        {linksLoading ? (
          <div className="px-5 py-8 text-center">
            <p className="text-slate-400 text-sm">Loading shared links...</p>
          </div>
        ) : sharedLinks.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-slate-500 text-lg mb-1">No shared links</p>
            <p className="text-slate-600 text-sm">
              Share comparison results or reports to create shareable links.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="text-left px-5 py-3 font-medium">Label</th>
                  <th className="text-left px-5 py-3 font-medium">URL</th>
                  <th className="text-left px-5 py-3 font-medium">Created</th>
                  <th className="text-right px-5 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sharedLinks.map((link) => (
                  <tr
                    key={link.id}
                    className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors"
                  >
                    <td className="px-5 py-3 text-slate-200">{link.label}</td>
                    <td className="px-5 py-3">
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-xs font-mono truncate block max-w-xs"
                      >
                        {link.url}
                      </a>
                    </td>
                    <td className="px-5 py-3 text-slate-400">
                      {link.created_at
                        ? new Date(link.created_at).toLocaleDateString()
                        : "--"}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => handleDeleteLink(link.id)}
                        className="text-xs text-red-400 hover:text-red-300 transition-colors"
                      >
                        Delete
                      </button>
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
