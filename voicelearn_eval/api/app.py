"""FastAPI application factory."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from voicelearn_eval.core.config import ensure_data_dir, load_config
from voicelearn_eval.core.orchestrator import EvalOrchestrator
from voicelearn_eval.plugins.base import PluginRegistry
from voicelearn_eval.plugins.llm.lm_eval_harness import LMEvalHarnessPlugin
from voicelearn_eval.plugins.stt.open_asr import STTEvalPlugin
from voicelearn_eval.plugins.tts.quality import TTSEvalPlugin
from voicelearn_eval.storage.seed import seed_builtin_suites
from voicelearn_eval.storage.sqlite_storage import SQLiteStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application state."""
    # Load config
    config = load_config()
    db_override = os.environ.get("VOICELEARN_EVAL_DB_PATH")
    if db_override:
        config.db_path = Path(db_override)
    ensure_data_dir(config)

    # Initialize storage
    storage = SQLiteStorage(config.db_path)
    await storage.initialize()
    await seed_builtin_suites(storage)

    # Initialize plugins
    registry = PluginRegistry()
    registry.register(LMEvalHarnessPlugin())
    registry.register(STTEvalPlugin())
    registry.register(TTSEvalPlugin())
    registry.discover_plugins()

    # Initialize orchestrator and WebSocket manager
    from voicelearn_eval.api.websocket import ConnectionManager

    ws_manager = ConnectionManager()
    orchestrator = EvalOrchestrator(storage, registry)
    orchestrator.add_progress_listener(ws_manager.send_progress)

    # Initialize download service
    from voicelearn_eval.services.download import DownloadService

    download_service = DownloadService(storage, ws_manager)
    await download_service.reset_stale_downloads()

    # Store on app state
    app.state.config = config
    app.state.storage = storage
    app.state.registry = registry
    app.state.orchestrator = orchestrator
    app.state.ws_manager = ws_manager
    app.state.download_service = download_service

    yield

    # Cleanup
    await storage.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="VoiceLearn Eval API",
        version="0.1.0",
        description="Unified AI model evaluation for educational voice interaction",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3200",
            "http://127.0.0.1:3200",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    # Register route modules
    from voicelearn_eval.api.routes import (
        baselines,
        compare,
        grade_matrix,
        models,
        reports,
        runs,
        share,
        suites,
        test_sets,
        trends,
    )

    app.include_router(models.router, prefix="/api/eval", tags=["Models"])
    app.include_router(suites.router, prefix="/api/eval", tags=["Suites"])
    app.include_router(runs.router, prefix="/api/eval", tags=["Runs"])
    app.include_router(compare.router, prefix="/api/eval", tags=["Compare"])
    app.include_router(grade_matrix.router, prefix="/api/eval", tags=["Grade Matrix"])
    app.include_router(trends.router, prefix="/api/eval", tags=["Trends"])
    app.include_router(baselines.router, prefix="/api/eval", tags=["Baselines"])
    app.include_router(reports.router, prefix="/api/eval", tags=["Reports"])
    app.include_router(test_sets.router, prefix="/api/eval", tags=["Test Sets"])
    app.include_router(share.router, prefix="/api/eval", tags=["Share"])

    # WebSocket endpoint for live progress
    @app.websocket("/api/eval/ws")
    async def websocket_endpoint(websocket: WebSocket):
        manager = app.state.ws_manager
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app
