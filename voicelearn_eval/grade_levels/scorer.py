"""Grade-level scoring: tier scores, pass/fail, and overall education score."""


from voicelearn_eval.core.models import GradeLevelRating

from .tiers import DEFAULT_THRESHOLD, TIER_ORDER, TIER_WEIGHTS


def calculate_tier_score(
    task_results: list[dict], tier: str
) -> tuple[float, list[dict]]:
    """Calculate weighted average score for tasks in a given tier.

    Returns (score, task_breakdown) where score is 0-100 and
    task_breakdown is a list of {task_name, score, weight} dicts.
    """
    tier_tasks = [
        r for r in task_results
        if r.get("education_tier") == tier and r.get("score") is not None
    ]

    if not tier_tasks:
        return 0.0, []

    total_weight = sum(t.get("weight", 1.0) for t in tier_tasks)
    if total_weight == 0:
        return 0.0, []

    weighted_sum = sum(
        t["score"] * t.get("weight", 1.0) for t in tier_tasks
    )
    score = weighted_sum / total_weight

    breakdown = [
        {
            "task_name": t.get("task_name", t.get("name", "Unknown")),
            "score": t["score"],
            "weight": t.get("weight", 1.0),
        }
        for t in tier_tasks
    ]

    return score, breakdown


def assess_tier(score: float, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """Determine if a tier score passes the threshold."""
    return score >= threshold


def get_max_passing_tier(
    tier_scores: dict[str, float],
    threshold: float = DEFAULT_THRESHOLD,
) -> str | None:
    """Get the highest tier where score >= threshold.

    Sequential: model must pass all lower tiers to earn a higher tier.
    """
    max_tier = None
    for tier in TIER_ORDER:
        tier_key = tier.value
        if tier_key in tier_scores and assess_tier(tier_scores[tier_key], threshold):
            max_tier = tier_key
        else:
            break  # Must pass sequentially
    return max_tier


def calculate_overall_education_score(tier_scores: dict[str, float]) -> float:
    """Calculate weighted overall education score across tiers.

    Lower tiers weighted more heavily because foundational capability
    matters most for educational contexts.
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for tier in TIER_ORDER:
        tier_key = tier.value
        if tier_key in tier_scores:
            weight = TIER_WEIGHTS.get(tier, 1.0)
            weighted_sum += tier_scores[tier_key] * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0

    return weighted_sum / total_weight


def compute_grade_level_rating(
    model_id: str,
    run_id: str,
    task_results: list[dict],
    threshold: float = DEFAULT_THRESHOLD,
) -> GradeLevelRating:
    """Compute the full grade-level rating from task results.

    Args:
        model_id: Model being rated
        run_id: The evaluation run that produced these results
        task_results: List of result dicts with education_tier, score, weight, task_name
        threshold: Pass/fail threshold (default 70%)

    Returns:
        GradeLevelRating with scores, max passing tier, and breakdown
    """
    tier_scores = {}
    tier_details = {}

    for tier in TIER_ORDER:
        tier_key = tier.value
        score, breakdown = calculate_tier_score(task_results, tier_key)
        if breakdown:  # Only include tiers that had tasks
            tier_scores[tier_key] = score
            tier_details[tier_key] = breakdown

    max_tier = get_max_passing_tier(tier_scores, threshold)
    overall = calculate_overall_education_score(tier_scores)

    return GradeLevelRating(
        model_id=model_id,
        run_id=run_id,
        tier_scores=tier_scores,
        max_passing_tier=max_tier,
        tier_details=tier_details,
        threshold=threshold,
        overall_education_score=overall,
    )
