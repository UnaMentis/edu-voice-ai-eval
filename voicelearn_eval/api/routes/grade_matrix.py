"""Grade-level matrix endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.grade_levels.scorer import compute_grade_level_rating
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/grade-matrix")
async def get_grade_matrix(
    model_id: str | None = None,
    storage: BaseStorage = Depends(get_storage),
):
    """Get grade-level matrix for one or all models."""
    if model_id:
        model = await storage.get_model(model_id)
        if not model:
            raise HTTPException(404, f"Model not found: {model_id}")
        models = [model]
    else:
        models = await storage.list_models(limit=50)

    matrix = []
    for model in models:
        runs = await storage.list_runs(
            filters={"model_id": model["id"], "status": "completed"},
            limit=1,
        )
        if not runs:
            continue

        run = runs[0]
        # Try to get grade info from overall_metrics
        metrics = run.get("overall_metrics")
        if isinstance(metrics, str):
            try:
                metrics = json.loads(metrics)
            except (json.JSONDecodeError, TypeError):
                metrics = {}

        grade_info = metrics.get("grade_level") if metrics else None

        if not grade_info:
            # Recompute from results
            results = await storage.get_results_for_run(run["id"])
            if results:
                rating = compute_grade_level_rating(
                    model_id=model["id"],
                    run_id=run["id"],
                    task_results=results,
                )
                grade_info = rating.to_dict()

        if grade_info:
            matrix.append({
                "model": model,
                "run_id": run["id"],
                "grade_level": grade_info,
                "overall_score": run.get("overall_score"),
            })

    return {"matrix": matrix, "total": len(matrix)}


@router.get("/grade-matrix/{model_id}")
async def get_model_grade_detail(
    model_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    """Get detailed grade-level breakdown for a model."""
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")

    runs = await storage.list_runs(
        filters={"model_id": model_id, "status": "completed"},
        limit=5,
    )

    history = []
    for run in runs:
        results = await storage.get_results_for_run(run["id"])
        if results:
            rating = compute_grade_level_rating(
                model_id=model_id,
                run_id=run["id"],
                task_results=results,
            )
            history.append({
                "run_id": run["id"],
                "completed_at": run.get("completed_at"),
                "grade_level": rating.to_dict(),
                "overall_score": run.get("overall_score"),
            })

    return {"model": model, "history": history}
