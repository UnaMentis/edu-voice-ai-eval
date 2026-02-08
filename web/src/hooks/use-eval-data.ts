"use client";

// ──────────────────────────────────────────────────────────────
// React data-fetching hooks (lightweight SWR-style pattern)
// ──────────────────────────────────────────────────────────────

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api-client";
import type {
  EvalModel,
  EvalRun,
  BenchmarkSuite,
  TaskResult,
} from "@/types/evaluation";

// ── Generic helpers ──────────────────────────────────────────

interface AsyncState<T> {
  data: T;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

// ── useModels ────────────────────────────────────────────────

export function useModels(
  params?: Record<string, string>
): AsyncState<EvalModel[]> {
  const [models, setModels] = useState<EvalModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listModels(params);
      setModels(data.items);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data: models, loading, error, refresh };
}

// ── useRuns ──────────────────────────────────────────────────

export function useRuns(
  params?: Record<string, string>
): AsyncState<EvalRun[]> {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listRuns(params);
      setRuns(data.items);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data: runs, loading, error, refresh };
}

// ── useSuites ────────────────────────────────────────────────

export function useSuites(): AsyncState<BenchmarkSuite[]> {
  const [suites, setSuites] = useState<BenchmarkSuite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listSuites();
      setSuites(data.items);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data: suites, loading, error, refresh };
}

// ── useRunResults ────────────────────────────────────────────

export function useRunResults(runId: string | null): AsyncState<TaskResult[]> {
  const [results, setResults] = useState<TaskResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!runId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRunResults(runId);
      setResults(data.items);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data: results, loading, error, refresh };
}

// ── useGradeMatrix ───────────────────────────────────────────

export function useGradeMatrix(modelId?: string): AsyncState<any[]> {
  const [matrix, setMatrix] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getGradeMatrix(modelId);
      setMatrix(data.matrix);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [modelId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data: matrix, loading, error, refresh };
}

// ── useRun (single run with polling) ─────────────────────────

export function useRun(
  runId: string | null,
  /** Poll interval in ms while status is running/queued. 0 = no polling. */
  pollInterval = 3000
): AsyncState<EvalRun | null> {
  const [run, setRun] = useState<EvalRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!runId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRun(runId);
      setRun(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Auto-poll while the run is still active
  useEffect(() => {
    if (!runId || !pollInterval) return;
    if (
      run?.status &&
      !["pending", "queued", "running"].includes(run.status)
    ) {
      return; // terminal state — stop polling
    }

    const timer = setInterval(refresh, pollInterval);
    return () => clearInterval(timer);
  }, [runId, pollInterval, run?.status, refresh]);

  return { data: run, loading, error, refresh };
}
