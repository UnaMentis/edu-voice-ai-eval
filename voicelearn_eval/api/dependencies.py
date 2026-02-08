"""FastAPI dependency injection helpers."""

from fastapi import Request

from voicelearn_eval.core.config import AppConfig
from voicelearn_eval.core.orchestrator import EvalOrchestrator
from voicelearn_eval.plugins.base import PluginRegistry
from voicelearn_eval.storage.base import BaseStorage


def get_storage(request: Request) -> BaseStorage:
    return request.app.state.storage


def get_config(request: Request) -> AppConfig:
    return request.app.state.config


def get_registry(request: Request) -> PluginRegistry:
    return request.app.state.registry


def get_orchestrator(request: Request) -> EvalOrchestrator:
    return request.app.state.orchestrator
