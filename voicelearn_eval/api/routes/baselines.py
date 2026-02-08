"""Baseline management endpoints."""


from fastapi import APIRouter, Depends, HTTPException

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
