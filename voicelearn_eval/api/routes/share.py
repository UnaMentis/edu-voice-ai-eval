"""Shared report endpoints."""

import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from voicelearn_eval.api.dependencies import get_storage
from voicelearn_eval.core.schemas import ShareCreate
from voicelearn_eval.storage.base import BaseStorage

router = APIRouter()


@router.post("/share", status_code=201)
async def create_share_link(
    body: ShareCreate,
    storage: BaseStorage = Depends(get_storage),
):
    """Create a shareable link for a report."""
    token = secrets.token_urlsafe(24)
    expires_at = None
    if body.expires_in_days:
        expires_at = (
            datetime.utcnow() + timedelta(days=body.expires_in_days)
        ).isoformat()

    report_id = await storage.create_shared_report({
        "token": token,
        "report_type": body.report_type,
        "report_config": body.report_config,
        "expires_at": expires_at,
    })

    return {
        "token": token,
        "url": f"/share/{token}",
        "expires_at": expires_at,
        "report_id": report_id,
    }


@router.get("/share/{token}")
async def get_shared_report(
    token: str,
    storage: BaseStorage = Depends(get_storage),
):
    """Access a shared report by token."""
    report = await storage.get_shared_report(token)
    if not report:
        raise HTTPException(404, "Shared report not found or expired")

    # Check expiry
    expires_at = report.get("expires_at")
    if expires_at:
        try:
            exp = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > exp:
                raise HTTPException(410, "This shared report has expired")
        except ValueError:
            pass

    await storage.increment_share_views(token)
    return report
