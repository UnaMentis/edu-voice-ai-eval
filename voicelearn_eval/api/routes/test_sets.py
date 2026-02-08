"""Custom test set endpoints."""


from fastapi import APIRouter, Depends, HTTPException

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import CustomTestSetCreate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/test-sets")
async def list_test_sets(
    model_type: str | None = None,
    storage: BaseStorage = Depends(get_storage),
):
    test_sets = await storage.list_test_sets(model_type=model_type)
    return {"items": test_sets, "total": len(test_sets)}


@router.post("/test-sets", status_code=201)
async def create_test_set(
    body: CustomTestSetCreate,
    storage: BaseStorage = Depends(get_storage),
):
    ts_id = await storage.create_test_set(body.model_dump())
    ts = await storage.get_test_set(ts_id)
    return ts


@router.get("/test-sets/{test_set_id}")
async def get_test_set(
    test_set_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    ts = await storage.get_test_set(test_set_id)
    if not ts:
        raise HTTPException(404, f"Test set not found: {test_set_id}")
    return ts


@router.delete("/test-sets/{test_set_id}")
async def delete_test_set(
    test_set_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    ts = await storage.get_test_set(test_set_id)
    if not ts:
        raise HTTPException(404, f"Test set not found: {test_set_id}")
    await storage.delete_test_set(test_set_id)
    return {"status": "deleted", "id": test_set_id}
