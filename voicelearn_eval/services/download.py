"""Model download service for HuggingFace models."""

from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class DownloadService:
    """Manages model weight downloads from HuggingFace Hub."""

    def __init__(self, storage, ws_manager, cache_dir: Path | None = None):
        self.storage = storage
        self.ws_manager = ws_manager
        self.cache_dir = cache_dir or Path.home() / ".cache" / "huggingface" / "hub"
        self._active: dict[str, threading.Event] = {}  # model_id -> cancel_event

    async def reset_stale_downloads(self) -> None:
        """Reset any 'downloading' states left from a previous crash."""
        models = await self.storage.list_models(
            filters={"download_status": "downloading"}, limit=100, offset=0
        )
        for model in models:
            await self.storage.update_model(model["id"], {
                "download_status": "failed",
                "download_error": "Interrupted by server restart",
            })

    async def start_download(self, model_id: str) -> None:
        """Begin downloading model weights in the background."""
        model = await self.storage.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        if model.get("download_status") == "downloading":
            raise ValueError(f"Model {model_id} is already downloading")

        repo_id = model.get("source_uri")
        if not repo_id:
            raise ValueError(f"Model {model_id} has no source_uri (HuggingFace repo ID)")

        if model.get("source_type") != "huggingface":
            raise ValueError(f"Download only supported for HuggingFace models, got: {model.get('source_type')}")

        await self.storage.update_model(model_id, {
            "download_status": "downloading",
            "download_error": None,
            "download_progress": 0,
        })

        cancel_event = threading.Event()
        self._active[model_id] = cancel_event

        asyncio.create_task(self._run_download(model_id, repo_id, cancel_event))

    async def _run_download(
        self, model_id: str, repo_id: str, cancel_event: threading.Event
    ) -> None:
        """Execute the download in a background thread."""
        try:
            await self._broadcast(model_id, 0, "Starting download...")

            local_path = await asyncio.to_thread(
                self._download_sync, repo_id, cancel_event
            )

            if cancel_event.is_set():
                await self.storage.update_model(model_id, {
                    "download_status": "none",
                    "download_error": "Cancelled by user",
                    "download_progress": 0,
                })
                await self._broadcast(model_id, 0, "Download cancelled")
            else:
                await self.storage.update_model(model_id, {
                    "download_status": "cached",
                    "local_path": str(local_path),
                    "download_progress": 100,
                    "download_error": None,
                })
                await self._broadcast(model_id, 100, "Download complete")

        except Exception as e:
            logger.error("Download failed for %s: %s", model_id, e)
            await self.storage.update_model(model_id, {
                "download_status": "failed",
                "download_error": str(e),
            })
            await self._broadcast(model_id, 0, f"Failed: {e}")
        finally:
            self._active.pop(model_id, None)

    def _download_sync(
        self, repo_id: str, cancel_event: threading.Event
    ) -> str:
        """Synchronous download — runs in a thread."""
        from huggingface_hub import snapshot_download

        local_path = snapshot_download(
            repo_id=repo_id,
            cache_dir=str(self.cache_dir),
        )
        return local_path

    async def cancel_download(self, model_id: str) -> None:
        """Cancel an active download."""
        event = self._active.get(model_id)
        if event:
            event.set()

    async def get_status(self, model_id: str) -> dict:
        """Get download status for a model."""
        model = await self.storage.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        return {
            "model_id": model_id,
            "status": model.get("download_status", "none"),
            "local_path": model.get("local_path"),
            "error": model.get("download_error"),
            "progress": model.get("download_progress", 0),
            "is_active": model_id in self._active,
        }

    async def _broadcast(self, model_id: str, percent: float, message: str) -> None:
        """Broadcast download progress via WebSocket."""
        try:
            await self.ws_manager.broadcast({
                "type": "download_progress",
                "model_id": model_id,
                "percent": percent,
                "message": message,
            })
        except Exception:
            pass  # Don't fail download if broadcast fails
