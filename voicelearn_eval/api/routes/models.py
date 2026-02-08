"""Model management endpoints."""


from fastapi import APIRouter, Depends, HTTPException, Query

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import HuggingFaceImport, ModelCreate, ModelUpdate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.get("/models")
async def list_models(
    model_type: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    storage: BaseStorage = Depends(get_storage),
):
    filters = {}
    if model_type:
        filters["model_type"] = model_type
    models = await storage.list_models(filters=filters, limit=limit, offset=offset)
    total = await storage.count_models(filters=filters)
    return {"items": models, "total": total, "limit": limit, "offset": offset}


@router.post("/models", status_code=201)
async def create_model(
    body: ModelCreate,
    storage: BaseStorage = Depends(get_storage),
):
    model_id = await storage.create_model(body.model_dump())
    model = await storage.get_model(model_id)
    return model


@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    model = await storage.get_model(model_id)
    if not model:
        model = await storage.get_model_by_slug(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")
    return model


@router.patch("/models/{model_id}")
async def update_model(
    model_id: str,
    body: ModelUpdate,
    storage: BaseStorage = Depends(get_storage),
):
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")
    updates = body.model_dump(exclude_unset=True)
    if updates:
        await storage.update_model(model_id, updates)
    return await storage.get_model(model_id)


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    storage: BaseStorage = Depends(get_storage),
):
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")
    await storage.delete_model(model_id)
    return {"status": "deleted", "id": model_id}


@router.get("/models/{model_id}/runs")
async def get_model_runs(
    model_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    storage: BaseStorage = Depends(get_storage),
):
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")
    runs = await storage.list_runs(filters={"model_id": model_id}, limit=limit, offset=offset)
    total = await storage.count_runs(filters={"model_id": model_id})
    return {"items": runs, "total": total, "limit": limit, "offset": offset}


@router.post("/models/import-hf", status_code=201)
async def import_from_huggingface(
    body: HuggingFaceImport,
    storage: BaseStorage = Depends(get_storage),
):
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        info = api.model_info(body.repo_id)

        model_data = {
            "name": info.modelId.split("/")[-1] if "/" in info.modelId else info.modelId,
            "model_type": body.model_type,
            "source_type": "huggingface",
            "source_uri": body.repo_id,
            "deployment_target": body.deployment_target,
            "model_family": info.modelId.split("/")[0] if "/" in info.modelId else None,
            "tags": list(info.tags or [])[:20],
        }

        if info.safetensors:
            total_params = sum(info.safetensors.get("parameters", {}).values())
            if total_params:
                model_data["parameter_count_b"] = round(total_params / 1e9, 2)

        model_id = await storage.create_model(model_data)
        return await storage.get_model(model_id)

    except ImportError:
        raise HTTPException(
            501,
            "huggingface_hub not installed. Run: pip install huggingface_hub",
        )
    except Exception as e:
        raise HTTPException(400, f"Failed to import from HuggingFace: {e}")
