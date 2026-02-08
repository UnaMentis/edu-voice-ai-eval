"""WebSocket connection manager for live progress updates."""

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time run progress."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [
            ws for ws in self.active_connections if ws != websocket
        ]

    async def broadcast(self, data: dict[str, Any]):
        """Send data to all connected clients."""
        message = json.dumps(data)
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_progress(self, run_id: str, update) -> None:
        """Progress listener callback for the orchestrator."""
        await self.broadcast({
            "type": "progress",
            "run_id": run_id,
            "task_name": update.task_name,
            "task_index": update.task_index,
            "total_tasks": update.total_tasks,
            "percent_complete": update.percent_complete,
            "message": update.message,
        })
