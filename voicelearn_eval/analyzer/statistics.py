"""Statistical aggregation for evaluation results."""

import math


def aggregate_scores(results: list[dict]) -> dict:
    """Compute aggregate statistics from a list of task results.

    Each result dict should have at least 'score' (float or None).
    Returns dict with mean, median, std_dev, min, max, count, and confidence_interval_95.
    """
    scores = [r["score"] for r in results if r.get("score") is not None]
    if not scores:
        return {
            "mean": None,
            "median": None,
            "std_dev": None,
            "min": None,
            "max": None,
            "count": 0,
            "confidence_interval_95": None,
        }

    n = len(scores)
    mean = sum(scores) / n
    sorted_scores = sorted(scores)

    if n % 2 == 0:
        median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
    else:
        median = sorted_scores[n // 2]

    variance = sum((s - mean) ** 2 for s in scores) / max(n - 1, 1)
    std_dev = math.sqrt(variance)

    # 95% confidence interval (using z=1.96 for large samples)
    margin = 1.96 * std_dev / math.sqrt(n) if n > 1 else 0
    ci_95 = (round(mean - margin, 2), round(mean + margin, 2))

    return {
        "mean": round(mean, 2),
        "median": round(median, 2),
        "std_dev": round(std_dev, 2),
        "min": round(min(scores), 2),
        "max": round(max(scores), 2),
        "count": n,
        "confidence_interval_95": ci_95,
    }


def score_by_category(results: list[dict], category_key: str = "education_tier") -> dict[str, dict]:
    """Group results by a category and compute aggregate stats for each group.

    Args:
        results: List of task result dicts
        category_key: Key to group by (e.g., 'education_tier', 'task_name')

    Returns:
        Dict mapping category values to aggregate stats.
    """
    groups: dict[str, list[dict]] = {}
    for r in results:
        cat = r.get(category_key, "unknown")
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(r)

    return {cat: aggregate_scores(items) for cat, items in groups.items()}


def percentile(scores: list[float], p: float) -> float:
    """Calculate the p-th percentile of a list of scores (0-100)."""
    if not scores:
        return 0.0
    sorted_scores = sorted(scores)
    k = (p / 100) * (len(sorted_scores) - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_scores[int(k)]
    return sorted_scores[f] * (c - k) + sorted_scores[c] * (k - f)
