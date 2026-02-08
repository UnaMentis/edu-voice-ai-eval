"""Report generation and export endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import ExportRequest
from voicelearn_eval.storage.base import BaseStorage
from voicelearn_eval.vlef.exporter import export_vlef
from voicelearn_eval.vlef.importer import import_vlef

router = APIRouter()


@router.post("/export")
async def export_data(
    body: ExportRequest,
    storage: BaseStorage = Depends(get_storage),
):
    """Export evaluation data in VLEF or other formats."""
    if body.format != "vlef":
        raise HTTPException(400, f"Unsupported format: {body.format}. Use 'vlef'.")

    data = await export_vlef(
        storage=storage,
        run_ids=body.run_ids,
        model_id=body.model_id,
        export_all=not body.run_ids and not body.model_id,
    )
    return data


@router.post("/import")
async def import_data(
    data: dict,
    merge: bool = False,
    storage: BaseStorage = Depends(get_storage),
):
    """Import evaluation data from VLEF format."""
    if not data.get("format_version"):
        raise HTTPException(400, "Invalid VLEF data: missing format_version")

    summary = await import_vlef(storage=storage, data=data, merge=merge)
    return {"status": "imported", "summary": summary}
