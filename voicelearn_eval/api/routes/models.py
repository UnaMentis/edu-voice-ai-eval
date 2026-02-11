"""Model management endpoints."""


from fastapi import APIRouter, Depends, HTTPException, Query, Request

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


# --- HuggingFace search (must come before {model_id} routes) ---


@router.get("/models/search-hf")
async def search_huggingface(
    q: str = Query(..., min_length=1),
    task: str | None = None,
    sort: str = Query("downloads"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search HuggingFace Hub for models."""
    try:
        from huggingface_hub import HfApi

        hf_api = HfApi()
        kwargs: dict = {"search": q, "sort": sort, "limit": limit, "direction": -1}
        if task:
            kwargs["pipeline_tag"] = task

        models = list(hf_api.list_models(**kwargs))
        results = []
        for m in models:
            size_b = None
            if m.safetensors:
                total_params = sum(m.safetensors.get("parameters", {}).values())
                if total_params:
                    size_b = round(total_params / 1e9, 2)

            results.append({
                "repo_id": m.modelId,
                "name": m.modelId.split("/")[-1] if "/" in m.modelId else m.modelId,
                "author": m.modelId.split("/")[0] if "/" in m.modelId else None,
                "downloads": m.downloads or 0,
                "likes": m.likes or 0,
                "pipeline_tag": m.pipeline_tag,
                "tags": list(m.tags or [])[:10],
                "last_modified": m.lastModified.isoformat() if m.lastModified else None,
                "parameter_count_b": size_b,
            })

        return {"items": results, "total": len(results), "query": q}

    except ImportError:
        raise HTTPException(501, "huggingface_hub not installed")
    except Exception as e:
        raise HTTPException(400, f"HuggingFace search failed: {e}")


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


# --- Model CRUD (parameterized routes) ---


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


# --- Download management ---


@router.post("/models/{model_id}/download")
async def start_download(
    model_id: str,
    request: Request,
    storage: BaseStorage = Depends(get_storage),
):
    """Start downloading model weights from HuggingFace."""
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")

    download_service = request.app.state.download_service
    try:
        await download_service.start_download(model_id)
        return {"status": "downloading", "model_id": model_id}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/models/{model_id}/download-status")
async def get_download_status(
    model_id: str,
    request: Request,
    storage: BaseStorage = Depends(get_storage),
):
    """Check download status for a model."""
    download_service = request.app.state.download_service
    try:
        return await download_service.get_status(model_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/models/{model_id}/download/cancel")
async def cancel_download(
    model_id: str,
    request: Request,
    storage: BaseStorage = Depends(get_storage),
):
    """Cancel an in-progress download."""
    model = await storage.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model not found: {model_id}")

    download_service = request.app.state.download_service
    await download_service.cancel_download(model_id)
    return {"status": "cancelled", "model_id": model_id}
