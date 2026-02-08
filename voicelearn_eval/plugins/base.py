"""Plugin system: hook specs, base class, and registry."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

import pluggy

PROJECT_NAME = "voicelearn_eval"
hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


class EvalPluginType(str, Enum):
    LLM = "llm"
    STT = "stt"
    TTS = "tts"
    VAD = "vad"
    EMBEDDINGS = "embeddings"


@dataclass
class EvalPluginMetadata:
    """Metadata describing an evaluation plugin."""

    name: str
    plugin_id: str
    version: str
    description: str
    plugin_type: EvalPluginType
    upstream_project: str = ""
    upstream_url: str = ""
    upstream_license: str = ""
    supported_benchmarks: list[str] = field(default_factory=list)
    requires_gpu: bool = False


@dataclass
class ProgressUpdate:
    """Progress update emitted during evaluation."""

    run_id: str
    task_name: str
    task_index: int
    total_tasks: int
    percent_complete: float
    message: str = ""


class EvalHookSpec:
    """Hook specifications that plugins must implement."""

    @hookspec
    def get_plugin_info(self) -> EvalPluginMetadata:
        """Return plugin metadata."""

    @hookspec
    def get_supported_benchmarks(self) -> list[dict]:
        """Return list of supported benchmark definitions."""

    @hookspec
    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run evaluation and return results."""

    @hookspec
    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        """Validate that a model can be evaluated by this plugin.
        Returns (is_valid, message)."""


class BaseEvalPlugin(ABC):
    """Abstract base class for evaluation plugins."""

    plugin_id: str = ""
    plugin_type: EvalPluginType = EvalPluginType.LLM

    @abstractmethod
    def get_plugin_info(self) -> EvalPluginMetadata:
        """Return plugin metadata."""

    @abstractmethod
    def get_supported_benchmarks(self) -> list[dict]:
        """Return list of supported benchmark definitions."""

    @abstractmethod
    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run evaluation and return results."""

    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        """Validate model. Override for custom validation."""
        return True, "OK"

    @staticmethod
    def normalize_score(raw_value: float, metric_type: str) -> float:
        """Normalize a raw metric value to 0-100 scale.

        - accuracy (0-1) -> multiply by 100
        - wer (0-1, lower is better) -> (1 - wer) * 100
        - mos (1-5) -> (mos - 1) / 4 * 100
        """
        if metric_type in ("accuracy", "acc", "acc_norm", "exact_match", "f1"):
            return raw_value * 100 if raw_value <= 1.0 else raw_value
        elif metric_type in ("wer", "cer"):
            return (1.0 - raw_value) * 100
        elif metric_type in ("mos", "mos_utmos", "mos_wvmos"):
            return (raw_value - 1.0) / 4.0 * 100
        elif metric_type in ("per",):  # phoneme error rate
            return (1.0 - raw_value) * 100
        else:
            # Assume already 0-100 or pass through
            return raw_value

    @staticmethod
    def make_result(
        task_id: str,
        score: float,
        raw_score: float,
        raw_metric_name: str,
        metrics: dict | None = None,
        **kwargs,
    ) -> dict:
        """Create a standardized result dict."""
        result = {
            "task_id": task_id,
            "score": score,
            "raw_score": raw_score,
            "raw_metric_name": raw_metric_name,
            "metrics": metrics or {},
            "status": "completed",
        }
        result.update(kwargs)
        return result


class PluginRegistry:
    """Discovers and manages evaluation plugins."""

    def __init__(self):
        self._manager = pluggy.PluginManager(PROJECT_NAME)
        self._manager.add_hookspecs(EvalHookSpec)
        self._plugins: dict[str, BaseEvalPlugin] = {}

    def discover_plugins(self) -> None:
        """Discover plugins from entry points."""
        try:
            self._manager.load_setuptools_entrypoints("voicelearn_eval.plugins")
        except Exception:
            pass  # No entry points found, that's OK

        # Register any plugins that were loaded
        for plugin in self._manager.get_plugins():
            if hasattr(plugin, "get_plugin_info"):
                try:
                    info = plugin.get_plugin_info()
                    self._plugins[info.plugin_id] = plugin
                except Exception:
                    continue

    def register(self, plugin: BaseEvalPlugin) -> None:
        """Manually register a plugin."""
        info = plugin.get_plugin_info()
        self._plugins[info.plugin_id] = plugin
        try:
            self._manager.register(plugin)
        except ValueError:
            pass  # Already registered

    def get_plugin(self, plugin_id: str) -> BaseEvalPlugin | None:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    def get_plugins_for_type(self, plugin_type: str) -> list[BaseEvalPlugin]:
        """Get all plugins for a model type."""
        return [
            p
            for p in self._plugins.values()
            if hasattr(p, "plugin_type")
            and (p.plugin_type == plugin_type or p.plugin_type.value == plugin_type)
        ]

    def get_all_plugins(self) -> dict[str, BaseEvalPlugin]:
        """Get all registered plugins."""
        return dict(self._plugins)

    def get_all_benchmarks(self) -> list[dict]:
        """Get all benchmarks from all plugins."""
        benchmarks = []
        for plugin in self._plugins.values():
            try:
                benchmarks.extend(plugin.get_supported_benchmarks())
            except Exception:
                continue
        return benchmarks

    def find_plugin_for_benchmark(self, benchmark_id: str) -> BaseEvalPlugin | None:
        """Find which plugin handles a specific benchmark."""
        for plugin in self._plugins.values():
            try:
                for bench in plugin.get_supported_benchmarks():
                    if bench.get("id") == benchmark_id:
                        return plugin
            except Exception:
                continue
        return None

    def find_plugin_for_model_type(self, model_type: str) -> BaseEvalPlugin | None:
        """Find the first plugin that handles a model type."""
        plugins = self.get_plugins_for_type(model_type)
        return plugins[0] if plugins else None
