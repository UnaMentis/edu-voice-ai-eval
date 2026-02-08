"""Evaluation run endpoints."""



from fastapi import APIRouter, Depends, HTTPException, Query

from voicelearn_eval.api.dependencies import get_orchestrator, get_storage
from voicelearn_eval.core.orchestrator import EvalOrchestrator
from voicelearn_eval.core.schemas import RunCreate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/runs")
async def list_runs(
    model_id: str | None = None,
    suite_id: str | None = None,
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    storage: BaseStorage = Depends(get_storage),
):
    filters = {}
    if model_id:
        filters["model_id"] = model_id
    if suite_id:
        filters["suite_id"] = suite_id
    if status:
        filters["status"] = status
    runs = await storage.list_runs(filters=filters, limit=limit, offset=offset)
    # Enrich runs with model/suite names for display
    for run in runs:
        if run.get("model_id"):
            model = await storage.get_model(run["model_id"])
            run["model_name"] = model["name"] if model else "Unknown"
        if run.get("suite_id"):
            suite = await storage.get_suite(run["suite_id"])
            run["suite_name"] = suite["name"] if suite else "Unknown"
    total = await storage.count_runs(filters=filters)
    return {"items": runs, "total": total, "limit": limit, "offset": offset}


@router.post("/runs", status_code=201)
async def start_run(
    body: RunCreate,
    orchestrator: EvalOrchestrator = Depends(get_orchestrator),
):
    try:
        run_id = await orchestrator.start_evaluation(
            model_id=body.model_id,
            suite_id=body.suite_id,
            config=body.config,
            priority=body.priority,
            triggered_by=body.triggered_by,
        )
        return {"run_id": run_id, "status": "started"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/runs/{run_id}")
async def get_run(
    run_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    run = await storage.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {run_id}")
    return run


@router.get("/runs/{run_id}/results")
async def get_run_results(
    run_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    run = await storage.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {run_id}")
    results = await storage.get_results_for_run(run_id)
    return {"items": results, "total": len(results), "run_id": run_id}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: str,
    orchestrator: EvalOrchestrator = Depends(get_orchestrator),
    storage: BaseStorage = Depends(get_storage),
):
    run = await storage.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {run_id}")
    await orchestrator.cancel_run(run_id)
    return {"status": "cancelled", "run_id": run_id}


@router.delete("/runs/{run_id}")
async def delete_run(
    run_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    run = await storage.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Run not found: {run_id}")
    await storage.delete_run(run_id)
    return {"status": "deleted", "id": run_id}


@router.get("/queue")
async def get_queue(
    storage: BaseStorage = Depends(get_storage),
):
    queue = await storage.get_queue()
    return {"items": queue, "total": len(queue)}
