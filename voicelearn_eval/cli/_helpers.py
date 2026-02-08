"""Shared CLI helpers for async operations and output formatting."""

import asyncio
from pathlib import Path

from voicelearn_eval.core.config import AppConfig, ensure_data_dir, load_config
from voicelearn_eval.core.orchestrator import EvalOrchestrator
from voicelearn_eval.plugins.base import PluginRegistry
from voicelearn_eval.plugins.llm.lm_eval_harness import LMEvalHarnessPlugin
from voicelearn_eval.storage.seed import seed_builtin_suites
from voicelearn_eval.storage.sqlite_storage import SQLiteStorage


def run_sync(coro):
    """Run an async function synchronously for CLI commands."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def get_initialized_storage(
    config_path: str | None = None, db_path: str | None = None
) -> tuple[SQLiteStorage, AppConfig]:
    """Initialize storage with config."""
    config = load_config(config_path)
    if db_path:
        config.db_path = Path(db_path)
    ensure_data_dir(config)

    storage = SQLiteStorage(config.db_path)
    await storage.initialize()
    await seed_builtin_suites(storage)
    return storage, config


def get_plugin_registry() -> PluginRegistry:
    """Create and populate plugin registry."""
    registry = PluginRegistry()
    # Register built-in plugins
    registry.register(LMEvalHarnessPlugin())
    # Discover any installed plugins
    registry.discover_plugins()
    return registry


async def get_orchestrator(
    config_path: str | None = None, db_path: str | None = None
) -> tuple[EvalOrchestrator, SQLiteStorage, AppConfig]:
    """Get a fully initialized orchestrator."""
    storage, config = await get_initialized_storage(config_path, db_path)
    registry = get_plugin_registry()
    orchestrator = EvalOrchestrator(storage, registry)
    return orchestrator, storage, config
