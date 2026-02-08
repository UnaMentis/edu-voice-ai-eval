"use client";

// ──────────────────────────────────────────────────────────────
// StatCard — compact metric display used on dashboard summaries
// ──────────────────────────────────────────────────────────────

interface StatCardProps {
  /** Descriptive label shown above the value. */
  label: string;
  /** Primary metric value (string to allow formatted numbers, percentages, etc.). */
  value: string | number;
  /** Optional delta indicator, e.g. "+3.2 %" or "-0.5". */
  change?: string;
  /** When `change` is provided, colour the indicator accordingly. */
  changeType?: "positive" | "negative" | "neutral";
  /** Optional icon rendered to the left of the label. */
  icon?: React.ReactNode;
  className?: string;
}

const CHANGE_COLORS: Record<string, string> = {
  positive: "text-emerald-400",
  negative: "text-red-400",
  neutral: "text-slate-400",
};

const CHANGE_ARROWS: Record<string, string> = {
  positive: "\u2191", // up arrow
  negative: "\u2193", // down arrow
  neutral: "\u2192",  // right arrow
};

export function StatCard({
  label,
  value,
  change,
  changeType = "neutral",
  icon,
  className = "",
}: StatCardProps) {
  return (
    <div
      className={`rounded-xl border border-slate-800 bg-slate-900/60 p-5 ${className}`}
    >
      {/* Label row */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        {icon && <span className="text-slate-500">{icon}</span>}
        <span>{label}</span>
      </div>

      {/* Value + change row */}
      <div className="mt-2 flex items-end gap-2">
        <span className="text-2xl font-semibold tracking-tight text-slate-100">
          {value}
        </span>

        {change && (
          <span
            className={`mb-0.5 text-sm font-medium ${CHANGE_COLORS[changeType]}`}
          >
            {CHANGE_ARROWS[changeType]} {change}
          </span>
        )}
      </div>
    </div>
  );
}
