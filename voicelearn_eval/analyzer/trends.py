"""Historical trend analysis for model performance over time."""



def analyze_trends(
    runs: list[dict],
    window_size: int = 5,
) -> dict:
    """Analyze score trends over time for a set of runs.

    Args:
        runs: List of run dicts sorted by date, each with at least
              'overall_score', 'completed_at', 'model_id'.
        window_size: Number of runs for moving average calculation.

    Returns:
        Dict with trend data per model including direction, moving average, etc.
    """
    # Group by model
    by_model: dict[str, list[dict]] = {}
    for run in runs:
        mid = run.get("model_id", "unknown")
        if mid not in by_model:
            by_model[mid] = []
        by_model[mid].append(run)

    trends = {}
    for model_id, model_runs in by_model.items():
        # Sort by completion date
        model_runs.sort(key=lambda r: r.get("completed_at") or "")

        scores = [r.get("overall_score") for r in model_runs if r.get("overall_score") is not None]
        dates = [r.get("completed_at") for r in model_runs if r.get("overall_score") is not None]

        if len(scores) < 2:
            trends[model_id] = {
                "direction": "insufficient_data",
                "data_points": len(scores),
                "scores": scores,
                "dates": dates,
                "moving_average": scores,
                "change": None,
                "change_percent": None,
            }
            continue

        # Moving average
        moving_avg = _moving_average(scores, window_size)

        # Trend direction
        recent = scores[-min(3, len(scores)):]
        earlier = scores[:min(3, len(scores))]
        avg_recent = sum(recent) / len(recent)
        avg_earlier = sum(earlier) / len(earlier)

        if avg_recent > avg_earlier + 2:
            direction = "improving"
        elif avg_recent < avg_earlier - 2:
            direction = "declining"
        else:
            direction = "stable"

        change = round(scores[-1] - scores[0], 2)
        change_pct = round((change / scores[0]) * 100, 1) if scores[0] != 0 else 0

        trends[model_id] = {
            "direction": direction,
            "data_points": len(scores),
            "scores": scores,
            "dates": dates,
            "moving_average": moving_avg,
            "change": change,
            "change_percent": change_pct,
            "latest_score": scores[-1],
            "first_score": scores[0],
        }

    return trends


def _moving_average(values: list[float], window: int) -> list[float]:
    """Calculate simple moving average."""
    if len(values) <= window:
        return [round(sum(values[:i+1]) / (i+1), 2) for i in range(len(values))]

    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        window_vals = values[start:i + 1]
        result.append(round(sum(window_vals) / len(window_vals), 2))
    return result


def detect_anomalies(
    scores: list[float],
    std_threshold: float = 2.0,
) -> list[dict]:
    """Detect anomalous scores that deviate significantly from the trend.

    Args:
        scores: List of scores in chronological order.
        std_threshold: Number of standard deviations to consider anomalous.

    Returns:
        List of anomaly dicts with index, score, expected, and deviation.
    """
    if len(scores) < 4:
        return []

    import math

    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / (len(scores) - 1)
    std = math.sqrt(variance)

    if std == 0:
        return []

    anomalies = []
    for i, score in enumerate(scores):
        deviation = abs(score - mean) / std
        if deviation > std_threshold:
            anomalies.append({
                "index": i,
                "score": score,
                "expected": round(mean, 2),
                "deviation_std": round(deviation, 2),
                "direction": "above" if score > mean else "below",
            })

    return anomalies
