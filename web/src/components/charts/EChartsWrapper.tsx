"use client";

// ──────────────────────────────────────────────────────────────
// EChartsWrapper — thin wrapper around echarts-for-react
// Renders a single ECharts instance with the dark theme and
// a consistent dark-slate background.
// ──────────────────────────────────────────────────────────────

import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";

interface EChartsWrapperProps {
  /** A fully-formed ECharts option object. */
  option: EChartsOption;
  /** Chart height in pixels. Defaults to 300. */
  height?: number;
  /** Additional class names applied to the outer container. */
  className?: string;
  /** All other props are forwarded to ReactECharts. */
  [key: string]: any;
}

export default function EChartsWrapper({
  option,
  height = 300,
  className = "",
  ...rest
}: EChartsWrapperProps) {
  return (
    <div
      className={`overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 p-4 ${className}`}
    >
      <ReactECharts
        option={option}
        style={{ height }}
        theme="dark"
        opts={{ renderer: "canvas" }}
        {...rest}
      />
    </div>
  );
}
