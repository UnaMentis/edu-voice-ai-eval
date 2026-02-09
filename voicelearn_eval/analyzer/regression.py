"""Regression detection against baselines."""


class RegressionSeverity:
    """Severity levels for regressions."""
    NONE = "none"
    MINOR = "minor"        # < 5% decline
    MODERATE = "moderate"  # 5-15% decline
    SEVERE = "severe"      # > 15% decline
    CRITICAL = "critical"  # Dropped below passing threshold


def detect_regressions(
    current_results: list[dict],
    baseline_results: list[dict],
    threshold: float = 70.0,
) -> dict:
    """Compare current results against baseline to detect regressions.

    Args:
        current_results: Task results from the current run.
        baseline_results: Task results from the baseline run.
        threshold: Grade-level pass/fail threshold.

    Returns:
        Dict with overall regression info and per-task details.
    """
    # Index baseline by task name
    baseline_by_task: dict[str, dict] = {}
    for r in baseline_results:
        key = r.get("task_name") or r.get("benchmark_id") or ""
        if key:
            baseline_by_task[key] = r

    task_regressions = []
    total_delta = 0.0
    regression_count = 0

    for result in current_results:
        key = result.get("task_name") or result.get("benchmark_id") or ""
        current_score = result.get("score")
        if current_score is None or not key:
            continue

        baseline = baseline_by_task.get(key)
        if not baseline or baseline.get("score") is None:
            continue

        baseline_score = baseline["score"]
        delta = current_score - baseline_score
        total_delta += delta

        severity = _classify_severity(current_score, baseline_score, threshold)

        if severity != RegressionSeverity.NONE:
            regression_count += 1

        task_regressions.append({
            "task_name": key,
            "current_score": round(current_score, 2),
            "baseline_score": round(baseline_score, 2),
            "delta": round(delta, 2),
            "delta_percent": round((delta / baseline_score) * 100, 1) if baseline_score != 0 else 0,
            "severity": severity,
            "education_tier": result.get("education_tier"),
        })

    # Sort by severity (worst first)
    severity_order = {
        RegressionSeverity.CRITICAL: 0,
        RegressionSeverity.SEVERE: 1,
        RegressionSeverity.MODERATE: 2,
        RegressionSeverity.MINOR: 3,
        RegressionSeverity.NONE: 4,
    }
    task_regressions.sort(key=lambda t: severity_order.get(t["severity"], 99))

    matched_count = len(task_regressions)
    avg_delta = round(total_delta / matched_count, 2) if matched_count > 0 else 0

    # Overall severity
    severities = [t["severity"] for t in task_regressions]
    if RegressionSeverity.CRITICAL in severities:
        overall_severity = RegressionSeverity.CRITICAL
    elif RegressionSeverity.SEVERE in severities:
        overall_severity = RegressionSeverity.SEVERE
    elif regression_count > matched_count * 0.5:
        overall_severity = RegressionSeverity.MODERATE
    elif regression_count > 0:
        overall_severity = RegressionSeverity.MINOR
    else:
        overall_severity = RegressionSeverity.NONE

    return {
        "has_regression": regression_count > 0,
        "overall_severity": overall_severity,
        "regression_count": regression_count,
        "total_tasks_compared": matched_count,
        "average_delta": avg_delta,
        "tasks": task_regressions,
    }


def _classify_severity(
    current: float, baseline: float, threshold: float
) -> str:
    """Classify regression severity for a single task."""
    if current >= baseline:
        return RegressionSeverity.NONE

    delta_pct = ((baseline - current) / baseline) * 100 if baseline != 0 else 0

    # Critical: dropped below passing threshold when baseline was above
    if baseline >= threshold and current < threshold:
        return RegressionSeverity.CRITICAL

    if delta_pct > 15:
        return RegressionSeverity.SEVERE
    elif delta_pct > 5:
        return RegressionSeverity.MODERATE
    elif delta_pct > 0:
        return RegressionSeverity.MINOR

    return RegressionSeverity.NONE


def ci_exit_code(regression_result: dict) -> int:
    """Return CI-appropriate exit code based on regression analysis.

    Exit codes:
        0 — No regressions detected
        1 — Below threshold (minor/moderate regressions)
        2 — Evaluation failed (severe/critical regressions)
    """
    severity = regression_result.get("overall_severity", RegressionSeverity.NONE)
    if severity in (RegressionSeverity.CRITICAL, RegressionSeverity.SEVERE):
        return 2
    elif severity in (RegressionSeverity.MODERATE, RegressionSeverity.MINOR):
        return 1
    return 0
