"""Shared test fixtures."""

import asyncio

import pytest
import pytest_asyncio

from voicelearn_eval.plugins.base import (
    BaseEvalPlugin,
    EvalPluginMetadata,
    EvalPluginType,
    PluginRegistry,
)
from voicelearn_eval.storage.seed import seed_builtin_suites
from voicelearn_eval.storage.sqlite_storage import SQLiteStorage


class MockLLMPlugin(BaseEvalPlugin):
    """Mock plugin for testing without real model evaluation."""

    plugin_id = "mock_llm"
    plugin_type = EvalPluginType.LLM

    def get_plugin_info(self) -> EvalPluginMetadata:
        return EvalPluginMetadata(
            name="Mock LLM Plugin",
            plugin_id="mock_llm",
            version="0.1.0",
            description="Mock plugin for testing",
            plugin_type=EvalPluginType.LLM,
            supported_benchmarks=["mmlu", "hellaswag", "arc_easy"],
        )

    def get_supported_benchmarks(self) -> list[dict]:
        return [
            {"id": "mmlu", "name": "MMLU", "metric": "accuracy"},
            {"id": "hellaswag", "name": "HellaSwag", "metric": "accuracy"},
            {"id": "arc_easy", "name": "ARC Easy", "metric": "accuracy"},
        ]

    async def run_evaluation(self, model_spec, benchmark_ids, config, progress_callback=None):
        results = []
        for i, bid in enumerate(benchmark_ids):
            if progress_callback:
                await progress_callback(bid, i, len(benchmark_ids), f"Evaluating {bid}")
            results.append(self.make_result(
                task_id=bid,
                score=75.0 + i * 5,
                raw_score=0.75 + i * 0.05,
                raw_metric_name="accuracy",
            ))
        return results

    def validate_model(self, model_spec):
        if model_spec.get("model_type") == "llm":
            return True, "OK"
        return False, "Not an LLM model"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def storage(tmp_path):
    """Create a temporary SQLite storage for testing."""
    db_path = tmp_path / "test.db"
    s = SQLiteStorage(db_path)
    await s.initialize()
    yield s
    await s.close()


@pytest_asyncio.fixture
async def seeded_storage(storage):
    """Storage with built-in suites seeded."""
    await seed_builtin_suites(storage)
    return storage


@pytest.fixture
def mock_plugin():
    """Create a mock LLM plugin."""
    return MockLLMPlugin()


@pytest.fixture
def plugin_registry(mock_plugin):
    """Create a registry with mock plugin."""
    registry = PluginRegistry()
    registry.register(mock_plugin)
    return registry


@pytest.fixture
def sample_model():
    """Sample model data for testing."""
    return {
        "name": "Test Model",
        "model_type": "llm",
        "source_type": "local",
        "deployment_target": "server",
    }


@pytest.fixture
def sample_model_hf():
    """Sample HuggingFace model data."""
    return {
        "name": "Phi-3-mini",
        "model_type": "llm",
        "source_type": "huggingface",
        "source_uri": "microsoft/phi-3-mini-4k-instruct",
        "deployment_target": "server",
        "parameter_count_b": 3.8,
        "context_window": 4096,
    }
