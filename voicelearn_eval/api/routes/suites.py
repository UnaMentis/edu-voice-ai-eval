"""Benchmark suite endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import SuiteCreate, SuiteUpdate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/suites")
async def list_suites(
    storage: BaseStorage = Depends(get_storage),
):
    suites = await storage.list_suites()
    return {"items": suites, "total": len(suites)}


@router.post("/suites", status_code=201)
async def create_suite(
    body: SuiteCreate,
    storage: BaseStorage = Depends(get_storage),
):
    suite_id = await storage.create_suite(body.model_dump())
    suite = await storage.get_suite(suite_id)
    return suite


@router.get("/suites/{suite_id}")
async def get_suite(
    suite_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    suite = await storage.get_suite(suite_id)
    if not suite:
        suite = await storage.get_suite_by_slug(suite_id)
    if not suite:
        raise HTTPException(404, f"Suite not found: {suite_id}")
    return suite


@router.patch("/suites/{suite_id}")
async def update_suite(
    suite_id: str,
    body: SuiteUpdate,
    storage: BaseStorage = Depends(get_storage),
):
    suite = await storage.get_suite(suite_id)
    if not suite:
        raise HTTPException(404, f"Suite not found: {suite_id}")
    if suite.get("is_builtin"):
        raise HTTPException(400, "Cannot modify built-in suites")
    updates = body.model_dump(exclude_unset=True)
    if updates:
        await storage.update_suite(suite_id, updates)
    return await storage.get_suite(suite_id)


@router.delete("/suites/{suite_id}")
async def delete_suite(
    suite_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    suite = await storage.get_suite(suite_id)
    if not suite:
        raise HTTPException(404, f"Suite not found: {suite_id}")
    if suite.get("is_builtin"):
        raise HTTPException(400, "Cannot delete built-in suites")
    await storage.delete_suite(suite_id)
    return {"status": "deleted", "id": suite_id}


@router.get("/suites/{suite_id}/tasks")
async def get_suite_tasks(
    suite_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    suite = await storage.get_suite(suite_id)
    if not suite:
        raise HTTPException(404, f"Suite not found: {suite_id}")
    tasks = await storage.get_tasks_for_suite(suite_id)
    return {"items": tasks, "total": len(tasks)}
