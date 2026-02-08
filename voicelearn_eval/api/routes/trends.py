"""Trend analysis endpoints."""

import json

from fastapi import APIRouter, Depends, Query

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/trends")
async def get_trends(
    model_id: str | None = None,
    suite_id: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    storage: BaseStorage = Depends(get_storage),
):
    """Get score trends over time for models."""
    filters = {"status": "completed"}
    if model_id:
        filters["model_id"] = model_id
    if suite_id:
        filters["suite_id"] = suite_id

    runs = await storage.list_runs(filters=filters, limit=limit)

    # Group by model
    by_model: dict[str, list] = {}
    for run in runs:
        mid = run.get("model_id", "unknown")
        if mid not in by_model:
            by_model[mid] = []

        metrics = run.get("overall_metrics")
        if isinstance(metrics, str):
            try:
                metrics = json.loads(metrics)
            except (json.JSONDecodeError, TypeError):
                metrics = {}

        by_model[mid].append({
            "run_id": run["id"],
            "score": run.get("overall_score"),
            "completed_at": run.get("completed_at"),
            "suite_id": run.get("suite_id"),
            "grade_level": metrics.get("grade_level") if metrics else None,
        })

    # Sort each model's runs by date
    for mid in by_model:
        by_model[mid].sort(key=lambda r: r.get("completed_at") or "")

    return {"trends": by_model, "model_count": len(by_model)}
