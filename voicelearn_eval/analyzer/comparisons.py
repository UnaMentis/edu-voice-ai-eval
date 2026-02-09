"""Multi-model comparison analysis."""

from .statistics import aggregate_scores, score_by_category


def compare_model_results(
    model_results: list[dict],
) -> dict:
    """Compare results across multiple models.

    Args:
        model_results: List of dicts, each with keys:
            - model: model dict
            - results: list of task result dicts
            - run: run dict (optional)

    Returns:
        Dict with comparison data including per-model stats, radar data,
        and delta from reference.
    """
    comparison = {
        "models": [],
        "radar_dimensions": _get_radar_dimensions(model_results),
        "reference_model_id": None,
        "summary": {},
    }

    # Find reference model if any
    for mr in model_results:
        if mr["model"].get("is_reference"):
            comparison["reference_model_id"] = mr["model"]["id"]
            break

    ref_stats = None
    for mr in model_results:
        stats = aggregate_scores(mr["results"])
        by_tier = score_by_category(mr["results"], "education_tier")

        model_entry = {
            "model_id": mr["model"]["id"],
            "model_name": mr["model"]["name"],
            "model_type": mr["model"]["model_type"],
            "overall": stats,
            "by_tier": by_tier,
            "parameter_count_b": mr["model"].get("parameter_count_b"),
            "run_id": mr.get("run", {}).get("id") if mr.get("run") else None,
            "overall_score": mr.get("run", {}).get("overall_score") if mr.get("run") else stats.get("mean"),
        }

        # Delta from reference
        if comparison["reference_model_id"] and mr["model"]["id"] != comparison["reference_model_id"]:
            if ref_stats is None:
                # Find reference stats
                for ref_mr in model_results:
                    if ref_mr["model"]["id"] == comparison["reference_model_id"]:
                        ref_stats = aggregate_scores(ref_mr["results"])
                        break
            if ref_stats and ref_stats["mean"] is not None and stats["mean"] is not None:
                model_entry["delta_from_reference"] = round(stats["mean"] - ref_stats["mean"], 2)

        comparison["models"].append(model_entry)

    # Sort by overall score descending
    comparison["models"].sort(
        key=lambda m: m.get("overall_score") or m["overall"]["mean"] or 0,
        reverse=True,
    )

    # Summary
    if comparison["models"]:
        comparison["summary"] = {
            "best_model": comparison["models"][0]["model_name"],
            "best_score": comparison["models"][0].get("overall_score") or comparison["models"][0]["overall"]["mean"],
            "model_count": len(comparison["models"]),
        }

    return comparison


def _get_radar_dimensions(model_results: list[dict]) -> list[str]:
    """Extract radar chart dimensions from results.

    Uses education tiers as primary dimensions, falling back to task names.
    """
    tiers = set()
    for mr in model_results:
        for r in mr["results"]:
            tier = r.get("education_tier")
            if tier:
                tiers.add(tier)

    if tiers:
        order = ["elementary", "high_school", "undergraduate", "graduate"]
        return sorted(tiers, key=lambda t: order.index(t) if t in order else 99)

    # Fallback to task names
    task_names = set()
    for mr in model_results:
        for r in mr["results"]:
            name = r.get("task_name")
            if name:
                task_names.add(name)
    return sorted(task_names)


def build_radar_data(model_results: list[dict], dimensions: list[str]) -> list[dict]:
    """Build radar chart data for each model across dimensions.

    Returns list of {model_name, model_id, values: [score_per_dimension]}.
    """
    radar_data = []
    for mr in model_results:
        # Group scores by dimension
        dim_scores: dict[str, list[float]] = {d: [] for d in dimensions}
        for r in mr["results"]:
            dim = r.get("education_tier") or r.get("task_name", "")
            if dim in dim_scores and r.get("score") is not None:
                dim_scores[dim].append(r["score"])

        values = []
        for d in dimensions:
            scores = dim_scores.get(d, [])
            values.append(round(sum(scores) / len(scores), 1) if scores else 0)

        radar_data.append({
            "model_name": mr["model"]["name"],
            "model_id": mr["model"]["id"],
            "values": values,
        })

    return radar_data
