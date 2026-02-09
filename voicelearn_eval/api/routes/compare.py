"""Model comparison endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/compare")
async def compare_runs(
    run_ids: str = Query(..., description="Comma-separated run IDs"),
    storage: BaseStorage = Depends(get_storage),
):
    """Compare results across multiple evaluation runs."""
    ids = [r.strip() for r in run_ids.split(",") if r.strip()]
    if len(ids) < 2:
        raise HTTPException(400, "At least 2 run IDs required for comparison")
    if len(ids) > 5:
        raise HTTPException(400, "Maximum 5 runs can be compared at once")

    comparisons = []
    for run_id in ids:
        run = await storage.get_run(run_id)
        if not run:
            raise HTTPException(404, f"Run not found: {run_id}")
        results = await storage.get_results_for_run(run_id)
        model = await storage.get_model(run["model_id"]) if run.get("model_id") else None
        comparisons.append({
            "run": run,
            "model": model,
            "results": results,
        })

    return {"comparisons": comparisons, "run_count": len(comparisons)}


@router.get("/compare/models")
async def compare_models(
    model_ids: str = Query(..., description="Comma-separated model IDs"),
    suite_id: str | None = Query(None, description="Filter by suite"),
    storage: BaseStorage = Depends(get_storage),
):
    """Compare latest results for multiple models."""
    ids = [m.strip() for m in model_ids.split(",") if m.strip()]
    if len(ids) < 2:
        raise HTTPException(400, "At least 2 model IDs required")

    comparisons = []
    for model_id in ids:
        model = await storage.get_model(model_id)
        if not model:
            raise HTTPException(404, f"Model not found: {model_id}")

        filters = {"model_id": model_id, "status": "completed"}
        if suite_id:
            filters["suite_id"] = suite_id
        runs = await storage.list_runs(filters=filters, limit=1)
        latest_run = runs[0] if runs else None
        results = []
        if latest_run:
            results = await storage.get_results_for_run(latest_run["id"])

        comparisons.append({
            "model": model,
            "latest_run": latest_run,
            "results": results,
        })

    # Use analyzer for structured comparison
    from voicelearn_eval.analyzer.comparisons import build_radar_data, compare_model_results

    analysis = compare_model_results(comparisons)
    radar = build_radar_data(comparisons, analysis.get("radar_dimensions", []))

    return {
        "comparisons": comparisons,
        "model_count": len(comparisons),
        "analysis": analysis,
        "radar": radar,
    }


@router.get("/compare/recommendations")
async def compare_recommendations(
    model_ids: str = Query(..., description="Comma-separated model IDs"),
    storage: BaseStorage = Depends(get_storage),
):
    """Get deployment recommendations for multiple models."""
    ids = [m.strip() for m in model_ids.split(",") if m.strip()]

    from voicelearn_eval.analyzer.recommendations import compare_recommendations, recommend_deployment

    recs = []
    for model_id in ids:
        model = await storage.get_model(model_id)
        if not model:
            raise HTTPException(404, f"Model not found: {model_id}")

        runs = await storage.list_runs(filters={"model_id": model_id, "status": "completed"}, limit=1)
        run = runs[0] if runs else None

        grade_rating = None
        if run:
            metrics = run.get("overall_metrics")
            if isinstance(metrics, str):
                try:
                    metrics = json.loads(metrics)
                except (json.JSONDecodeError, TypeError):
                    metrics = {}
            grade_rating = metrics.get("grade_level") if metrics else None

        rec = recommend_deployment(model=model, run=run, grade_rating=grade_rating)
        rec["model_name"] = model["name"]
        rec["model_id"] = model["id"]
        recs.append(rec)

    summary = compare_recommendations(recs)
    return {"recommendations": recs, "summary": summary}
