"use client";

import type { ModelType, RunStatus } from "@/types/evaluation";

// ──────────────────────────────────────────────────────────────
// Badge — colour-coded pill for model types & run statuses
// ──────────────────────────────────────────────────────────────

/** Colour map keyed by ModelType. */
const MODEL_TYPE_STYLES: Record<ModelType, string> = {
  llm: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  stt: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  tts: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  vad: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  embeddings: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
};

/** Colour map keyed by RunStatus. */
const STATUS_STYLES: Record<RunStatus, string> = {
  completed: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  running: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  queued: "bg-sky-500/20 text-sky-400 border-sky-500/30",
  pending: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  failed: "bg-red-500/20 text-red-400 border-red-500/30",
  cancelled: "bg-slate-500/20 text-slate-500 border-slate-500/30",
};

// ── Shared base classes ──────────────────────────────────────

const BASE =
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap";

// ── ModelTypeBadge ───────────────────────────────────────────

interface ModelTypeBadgeProps {
  type: ModelType;
  className?: string;
}

export function ModelTypeBadge({ type, className = "" }: ModelTypeBadgeProps) {
  return (
    <span className={`${BASE} ${MODEL_TYPE_STYLES[type] ?? ""} ${className}`}>
      {type.toUpperCase()}
    </span>
  );
}

// ── StatusBadge ──────────────────────────────────────────────

interface StatusBadgeProps {
  status: RunStatus;
  className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const dot =
    status === "running" ? (
      <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-yellow-400" />
    ) : null;

  return (
    <span className={`${BASE} ${STATUS_STYLES[status] ?? ""} ${className}`}>
      {dot}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

// ── Generic Badge ────────────────────────────────────────────

type BadgeVariant = "default" | "info" | "success" | "warning" | "danger";

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  default: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  info: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  success: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  warning: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  danger: "bg-red-500/20 text-red-400 border-red-500/30",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export function Badge({
  children,
  variant = "default",
  className = "",
}: BadgeProps) {
  return (
    <span className={`${BASE} ${VARIANT_STYLES[variant]} ${className}`}>
      {children}
    </span>
  );
}
