"""Baseline management endpoints."""


from fastapi import APIRouter, Depends, HTTPException, Query

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import BaselineCreate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/baselines")
async def list_baselines(
    model_id: str | None = None,
    suite_id: str | None = None,
    storage: BaseStorage = Depends(get_storage),
):
    baselines = await storage.list_baselines(model_id=model_id, suite_id=suite_id)
    return {"items": baselines, "total": len(baselines)}


@router.post("/baselines", status_code=201)
async def create_baseline(
    body: BaselineCreate,
    storage: BaseStorage = Depends(get_storage),
):
    # Validate references
    model = await storage.get_model(body.model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {body.model_id}")

    run = await storage.get_run(body.run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {body.run_id}")

    baseline_id = await storage.create_baseline(body.model_dump())
    baseline = await storage.get_baseline(baseline_id)
    return baseline


@router.get("/baselines/{baseline_id}")
async def get_baseline(
    baseline_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    baseline = await storage.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(404, f"Baseline not found: {baseline_id}")
    return baseline


@router.delete("/baselines/{baseline_id}")
async def delete_baseline(
    baseline_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    baseline = await storage.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(404, f"Baseline not found: {baseline_id}")
    await storage.delete_baseline(baseline_id)
    return {"status": "deleted", "id": baseline_id}


@router.get("/baselines/{baseline_id}/check")
async def check_regression(
    baseline_id: str,
    run_id: str = Query(..., description="Run ID to compare against baseline"),
    storage: BaseStorage = Depends(get_storage),
):
    """Check a run against a baseline for regressions."""
    baseline = await storage.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(404, f"Baseline not found: {baseline_id}")

    run = await storage.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {run_id}")

    baseline_run_id = baseline.get("run_id")
    if not baseline_run_id:
        raise HTTPException(400, "Baseline has no associated run")

    baseline_results = await storage.get_results_for_run(baseline_run_id)
    current_results = await storage.get_results_for_run(run_id)

    from voicelearn_eval.analyzer.regression import ci_exit_code, detect_regressions

    regression = detect_regressions(current_results, baseline_results)
    regression["exit_code"] = ci_exit_code(regression)

    return regression
