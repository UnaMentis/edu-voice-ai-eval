"use client";

// ──────────────────────────────────────────────────────────────
// ProgressBar — horizontal progress indicator
// ──────────────────────────────────────────────────────────────

type ProgressVariant = "default" | "success" | "warning" | "danger" | "info";

const BAR_COLORS: Record<ProgressVariant, string> = {
  default: "bg-blue-500",
  success: "bg-emerald-500",
  warning: "bg-yellow-500",
  danger: "bg-red-500",
  info: "bg-cyan-500",
};

interface ProgressBarProps {
  /** Progress percentage (0 – 100). Clamped internally. */
  value: number;
  /** Visual variant controlling the fill colour. */
  variant?: ProgressVariant;
  /** Optional label shown to the right of the bar (e.g. "72 %"). */
  label?: string;
  /** Bar height class — defaults to `h-2`. */
  size?: "sm" | "md" | "lg";
  /** Animate the bar width transitions. */
  animate?: boolean;
  className?: string;
}

const SIZE_CLASSES: Record<string, string> = {
  sm: "h-1.5",
  md: "h-2.5",
  lg: "h-4",
};

export function ProgressBar({
  value,
  variant = "default",
  label,
  size = "md",
  animate = true,
  className = "",
}: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Track */}
      <div
        className={`flex-1 overflow-hidden rounded-full bg-slate-800 ${SIZE_CLASSES[size]}`}
      >
        {/* Fill */}
        <div
          className={`${SIZE_CLASSES[size]} rounded-full ${BAR_COLORS[variant]} ${
            animate ? "transition-all duration-500 ease-out" : ""
          }`}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {/* Optional label */}
      {label !== undefined && (
        <span className="min-w-[3ch] text-right text-xs font-medium text-slate-400">
          {label}
        </span>
      )}
    </div>
  );
}
