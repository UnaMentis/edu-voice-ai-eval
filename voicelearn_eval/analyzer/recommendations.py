"""Automated deployment recommendations based on evaluation results."""


DEPLOYMENT_TARGETS = {
    "on-device": {
        "max_params_b": 3.0,
        "max_size_gb": 4.0,
        "min_score": 60.0,
        "description": "Mobile/edge device deployment",
    },
    "server": {
        "max_params_b": 70.0,
        "max_size_gb": 150.0,
        "min_score": 70.0,
        "description": "Server-side deployment",
    },
    "cloud-api": {
        "max_params_b": None,  # No limit
        "max_size_gb": None,
        "min_score": 75.0,
        "description": "Cloud API deployment",
    },
}


def recommend_deployment(
    model: dict,
    run: dict | None = None,
    results: list[dict] | None = None,
    grade_rating: dict | None = None,
) -> dict:
    """Generate deployment recommendation for a model.

    Args:
        model: Model dict with type, parameters, size, etc.
        run: Latest completed run dict (optional).
        results: Task results (optional).
        grade_rating: Grade-level rating dict (optional).

    Returns:
        Dict with recommended_target, suitability scores, warnings, and rationale.
    """
    score = run.get("overall_score", 0) if run else 0
    params = model.get("parameter_count_b")
    size = model.get("model_size_gb")
    max_tier = grade_rating.get("max_passing_tier") if grade_rating else None

    suitable_targets = []
    warnings = []
    rationale = []

    for target, constraints in DEPLOYMENT_TARGETS.items():
        suitability = 100.0
        target_warnings = []

        # Check parameter count
        if params and constraints["max_params_b"] is not None:
            if params > constraints["max_params_b"]:
                suitability -= 40
                target_warnings.append(
                    f"Model has {params}B params, target max is {constraints['max_params_b']}B"
                )

        # Check model size
        if size and constraints["max_size_gb"] is not None:
            if size > constraints["max_size_gb"]:
                suitability -= 30
                target_warnings.append(
                    f"Model is {size}GB, target max is {constraints['max_size_gb']}GB"
                )

        # Check score threshold
        if score < constraints["min_score"]:
            suitability -= 30
            target_warnings.append(
                f"Score {score:.1f} below target minimum {constraints['min_score']}"
            )

        suitable_targets.append({
            "target": target,
            "suitability": max(0, round(suitability, 1)),
            "description": constraints["description"],
            "warnings": target_warnings,
        })

    # Sort by suitability descending
    suitable_targets.sort(key=lambda t: t["suitability"], reverse=True)
    recommended = suitable_targets[0]["target"] if suitable_targets else "server"

    # Grade-level specific recommendations
    if max_tier:
        tier_labels = {
            "elementary": "Elementary (Gr 5-8)",
            "high_school": "High School (Gr 9-12)",
            "undergraduate": "Undergraduate",
            "graduate": "Graduate",
        }
        rationale.append(f"Certified up to {tier_labels.get(max_tier, max_tier)} level")
    else:
        warnings.append("Model has not passed any education tier threshold")

    # Model type specific
    model_type = model.get("model_type", "")
    if model_type == "stt" and params and params > 1.5:
        warnings.append("Large STT models may have high latency for real-time on-device use")
    if model_type == "tts" and not model.get("quantization"):
        rationale.append("Consider quantization for faster TTS inference")

    return {
        "recommended_target": recommended,
        "targets": suitable_targets,
        "score": score,
        "max_education_tier": max_tier,
        "warnings": warnings,
        "rationale": rationale,
    }


def compare_recommendations(model_recommendations: list[dict]) -> dict:
    """Compare deployment recommendations across multiple models.

    Args:
        model_recommendations: List of recommendation dicts from recommend_deployment().

    Returns:
        Summary comparison with best model per target and overall recommendation.
    """
    best_per_target: dict[str, dict | None] = {}

    for rec in model_recommendations:
        for target_info in rec.get("targets", []):
            target = target_info["target"]
            current_best = best_per_target.get(target)
            if current_best is None or target_info["suitability"] > current_best["suitability"]:
                best_per_target[target] = {
                    **target_info,
                    "model_name": rec.get("model_name", "Unknown"),
                    "score": rec.get("score", 0),
                }

    return {
        "best_per_target": best_per_target,
        "total_models": len(model_recommendations),
    }
