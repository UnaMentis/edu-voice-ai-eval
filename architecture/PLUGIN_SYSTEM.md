# Plugin System Architecture

The evaluation system uses a plugin architecture to wrap upstream evaluation tools (lm-evaluation-harness, Open ASR, UTMOS, etc.). This keeps the core system tool-agnostic and allows new evaluation backends to be added without modifying core code.

## Design

Based on [pluggy](https://pluggy.readthedocs.io/), the same framework used by pytest and the UnaMentis curriculum importers. Plugins are discovered via Python entry points (PEP 621) and can also be loaded from local directories.

## Plugin Types

Each plugin handles one model category:

| Type | What It Evaluates | Primary Upstream Tool |
|------|-------------------|----------------------|
| `llm` | Language models | lm-evaluation-harness |
| `stt` | Speech-to-text models | Open ASR Leaderboard, Picovoice |
| `tts` | Text-to-speech models | UTMOS, WVMOS |
| `vad` | Voice activity detection | Custom pipeline |
| `embeddings` | Embedding models | MTEB |

## Hook Specification

```python
# voicelearn_eval/plugins/base.py

import pluggy
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

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
    """Metadata about an evaluation plugin."""
    name: str                       # Human-readable name
    plugin_id: str                  # Unique identifier (e.g., "lm_eval_harness")
    version: str
    description: str
    plugin_type: EvalPluginType
    upstream_project: str           # e.g., "EleutherAI lm-evaluation-harness"
    upstream_url: str               # e.g., "https://github.com/EleutherAI/lm-evaluation-harness"
    upstream_license: str           # e.g., "MIT"
    supported_benchmarks: list[str] # Benchmark IDs this plugin can run
    requires_gpu: bool = False
    requires_network: bool = False
    estimated_vram_gb: Optional[float] = None


@dataclass
class ProgressUpdate:
    """Progress update from a running evaluation."""
    task_name: str
    task_index: int
    total_tasks: int
    percent_complete: float
    current_metric: Optional[str] = None
    current_value: Optional[float] = None
    message: Optional[str] = None


class EvalHookSpec:
    """Hook specifications that plugins implement."""

    @hookspec
    def get_plugin_info(self) -> EvalPluginMetadata:
        """Return metadata about this plugin."""
        ...

    @hookspec
    def get_supported_benchmarks(self) -> list[dict]:
        """Return benchmark definitions this plugin can run.

        Each dict contains:
            id: str - Unique benchmark ID
            name: str - Human-readable name
            description: str - What this benchmark tests
            metrics: list[str] - Metric names produced
            education_tier: Optional[str] - Education tier if applicable
            subject: Optional[str] - Subject area if applicable
            estimated_duration_minutes: Optional[float]
        """
        ...

    @hookspec
    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable[[ProgressUpdate], None],
    ) -> list[dict]:
        """Execute evaluation and return results.

        Args:
            model_spec: Model specification (from ModelSpec.to_dict())
            benchmark_ids: Which benchmarks to run
            config: Runtime configuration (GPU device, batch size, etc.)
            progress_callback: Called with ProgressUpdate during execution

        Returns:
            List of result dicts, one per benchmark:
                benchmark_id: str
                score: float (0-100 normalized)
                raw_score: float
                raw_metric_name: str
                metrics: dict (all metrics)
                latency_ms: Optional[float]
                throughput: Optional[float]
                memory_peak_mb: Optional[float]
                sample_audio_path: Optional[str] (TTS only)
                status: str ("completed" | "failed" | "skipped")
                error_message: Optional[str]
                duration_seconds: float
        """
        ...

    @hookspec
    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        """Check if this plugin can evaluate the given model.

        Returns:
            (is_valid, message) - message explains why if invalid
        """
        ...
```

## Base Plugin Class

```python
class BaseEvalPlugin(ABC):
    """Base class for evaluation plugins.

    Subclasses must implement the abstract methods. The base class provides
    common utilities for model loading, metric normalization, and error handling.
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        ...

    @property
    @abstractmethod
    def plugin_type(self) -> EvalPluginType:
        """What type of models this plugin evaluates."""
        ...

    @abstractmethod
    def get_plugin_info(self) -> EvalPluginMetadata:
        ...

    @abstractmethod
    def get_supported_benchmarks(self) -> list[dict]:
        ...

    @abstractmethod
    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable,
    ) -> list[dict]:
        ...

    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        """Default validation: check model type matches plugin type."""
        model_type = model_spec.get("model_type")
        if model_type != self.plugin_type.value:
            return False, f"Plugin {self.plugin_id} handles {self.plugin_type.value}, not {model_type}"
        return True, "OK"

    # Utility methods available to all plugins

    def normalize_score(self, raw_value: float, metric_name: str) -> float:
        """Normalize a raw metric to 0-100 scale.

        Different metrics have different scales:
        - accuracy (0.0-1.0) -> multiply by 100
        - WER (0.0-1.0, lower is better) -> (1 - wer) * 100
        - MOS (1.0-5.0) -> (mos - 1) / 4 * 100
        """
        normalizers = {
            "accuracy": lambda v: v * 100,
            "f1": lambda v: v * 100,
            "exact_match": lambda v: v * 100,
            "wer": lambda v: (1 - v) * 100,
            "cer": lambda v: (1 - v) * 100,
            "mos": lambda v: (v - 1) / 4 * 100,
            "mos_utmos": lambda v: (v - 1) / 4 * 100,
            "mos_wvmos": lambda v: (v - 1) / 4 * 100,
            "pronunciation_accuracy": lambda v: v * 100,
            "intelligibility_wer": lambda v: (1 - v) * 100,
        }
        normalizer = normalizers.get(metric_name, lambda v: v)
        return max(0.0, min(100.0, normalizer(raw_value)))

    def make_result(
        self,
        benchmark_id: str,
        raw_score: float,
        raw_metric_name: str,
        metrics: dict,
        **kwargs,
    ) -> dict:
        """Create a standardized result dict."""
        return {
            "benchmark_id": benchmark_id,
            "score": self.normalize_score(raw_score, raw_metric_name),
            "raw_score": raw_score,
            "raw_metric_name": raw_metric_name,
            "metrics": metrics,
            "status": "completed",
            **kwargs,
        }
```

## Plugin Registry

```python
class PluginRegistry:
    """Discovers and manages evaluation plugins."""

    def __init__(self):
        self._manager = pluggy.PluginManager(PROJECT_NAME)
        self._manager.add_hookspecs(EvalHookSpec)
        self._plugins: dict[str, BaseEvalPlugin] = {}

    def discover_plugins(self):
        """Discover plugins from entry points and local directory."""
        # 1. Entry point discovery (installed packages)
        for ep in importlib.metadata.entry_points(
            group="voicelearn_eval.plugins"
        ):
            plugin_class = ep.load()
            self.register(plugin_class())

        # 2. Local plugin discovery (plugins/ directory)
        self._discover_local_plugins()

    def register(self, plugin: BaseEvalPlugin):
        """Register a plugin instance."""
        self._manager.register(plugin)
        self._plugins[plugin.plugin_id] = plugin

    def get_plugin(self, plugin_id: str) -> Optional[BaseEvalPlugin]:
        return self._plugins.get(plugin_id)

    def get_plugins_for_type(self, model_type: EvalPluginType) -> list[BaseEvalPlugin]:
        return [p for p in self._plugins.values() if p.plugin_type == model_type]

    def get_all_benchmarks(self) -> list[dict]:
        """Collect all benchmarks from all plugins."""
        all_benchmarks = []
        for plugin in self._plugins.values():
            benchmarks = plugin.get_supported_benchmarks()
            for b in benchmarks:
                b["plugin_id"] = plugin.plugin_id
            all_benchmarks.extend(benchmarks)
        return all_benchmarks

    def find_plugin_for_benchmark(self, benchmark_id: str) -> Optional[BaseEvalPlugin]:
        """Find which plugin handles a given benchmark."""
        for plugin in self._plugins.values():
            supported = [b["id"] for b in plugin.get_supported_benchmarks()]
            if benchmark_id in supported:
                return plugin
        return None
```

## Built-In Plugins

### LLM Plugin: lm-evaluation-harness

```python
class LMEvalHarnessPlugin(BaseEvalPlugin):
    """Wraps EleutherAI's lm-evaluation-harness for LLM evaluation."""

    plugin_id = "lm_eval_harness"
    plugin_type = EvalPluginType.LLM

    # Maps our benchmark IDs to lm-eval-harness task names
    BENCHMARK_MAP = {
        # Education Tier 1 (Grades 5-8)
        "edu_tier1_mmlu_elementary": ["mmlu_elementary_mathematics", "mmlu_formal_logic"],
        "edu_tier1_arc_easy": ["arc_easy"],
        "edu_tier1_gsm8k": ["gsm8k"],

        # Education Tier 2 (Grades 9-12)
        "edu_tier2_mmlu_hs_bio": ["mmlu_high_school_biology"],
        "edu_tier2_mmlu_hs_chem": ["mmlu_high_school_chemistry"],
        "edu_tier2_mmlu_hs_phys": ["mmlu_high_school_physics"],
        "edu_tier2_mmlu_hs_math": ["mmlu_high_school_mathematics"],
        "edu_tier2_arc_challenge": ["arc_challenge"],

        # Education Tier 3 (Undergraduate)
        "edu_tier3_mmlu_college": ["mmlu_college_biology", "mmlu_college_chemistry",
                                    "mmlu_college_mathematics", "mmlu_college_physics",
                                    "mmlu_college_computer_science"],
        "edu_tier3_math": ["math"],
        "edu_tier3_mmlu_pro": ["mmlu_pro"],

        # Education Tier 4 (Graduate/PhD)
        "edu_tier4_mmlu_professional": ["mmlu_professional_medicine",
                                         "mmlu_professional_law",
                                         "mmlu_professional_accounting"],
        "edu_tier4_gpqa": ["gpqa"],

        # Standard (non-tiered)
        "standard_truthfulqa": ["truthfulqa_mc2"],
        "standard_hellaswag": ["hellaswag"],
        "standard_humaneval": ["humaneval"],
        "standard_ifeval": ["ifeval"],
    }

    async def run_evaluation(self, model_spec, benchmark_ids, config, progress_callback):
        """Run lm-evaluation-harness for the specified benchmarks.

        Execution modes:
        1. Python API (preferred): import lm_eval and call simple_evaluate()
        2. Subprocess (fallback): shell out to `lm_eval` CLI for isolation
        """
        results = []
        for i, benchmark_id in enumerate(benchmark_ids):
            progress_callback(ProgressUpdate(
                task_name=benchmark_id,
                task_index=i,
                total_tasks=len(benchmark_ids),
                percent_complete=i / len(benchmark_ids) * 100,
            ))

            tasks = self.BENCHMARK_MAP.get(benchmark_id, [])
            if not tasks:
                results.append(self.make_result(
                    benchmark_id, 0.0, "accuracy", {},
                    status="skipped", error_message=f"Unknown benchmark: {benchmark_id}",
                ))
                continue

            # Execute via lm-evaluation-harness
            # ... (see INTEGRATION_POINTS.md for full details)

        return results
```

### STT Plugin: Open ASR + Picovoice

```python
class STTEvalPlugin(BaseEvalPlugin):
    """Speech-to-text evaluation using Open ASR and Picovoice methodologies."""

    plugin_id = "stt_eval"
    plugin_type = EvalPluginType.STT

    BENCHMARKS = {
        "stt_librispeech_clean": {"dataset": "librispeech_asr", "split": "test.clean"},
        "stt_librispeech_other": {"dataset": "librispeech_asr", "split": "test.other"},
        "stt_common_voice": {"dataset": "mozilla-foundation/common_voice_16_1", "split": "test"},
        "stt_tedlium": {"dataset": "LIUM/tedlium", "split": "test"},
        "stt_edu_vocabulary": {"dataset": "custom", "path": "test_sets/stt/educational_vocabulary/"},
        "stt_edu_tier1": {"dataset": "custom", "path": "test_sets/stt/educational_vocabulary/tier1_elementary.json"},
        "stt_edu_tier2": {"dataset": "custom", "path": "test_sets/stt/educational_vocabulary/tier2_high_school.json"},
        "stt_edu_tier3": {"dataset": "custom", "path": "test_sets/stt/educational_vocabulary/tier3_undergraduate.json"},
        "stt_edu_tier4": {"dataset": "custom", "path": "test_sets/stt/educational_vocabulary/tier4_graduate.json"},
    }

    async def run_evaluation(self, model_spec, benchmark_ids, config, progress_callback):
        """Run STT evaluation: load audio, run inference, compute WER."""
        # Uses jiwer for WER computation
        # Supports HuggingFace models, Whisper variants, and API endpoints
        ...
```

### TTS Plugin: UTMOS + WVMOS + Pronunciation

```python
class TTSEvalPlugin(BaseEvalPlugin):
    """Text-to-speech evaluation with automated quality scoring."""

    plugin_id = "tts_eval"
    plugin_type = EvalPluginType.TTS

    BENCHMARKS = {
        "tts_quality_mos": {"metric": "mos", "description": "UTMOS + WVMOS averaged MOS"},
        "tts_intelligibility": {"metric": "wer", "description": "STT round-trip intelligibility"},
        "tts_pronunciation_edu": {"metric": "accuracy", "description": "Educational term pronunciation"},
        "tts_prosody": {"metric": "score", "description": "Pitch range and rate variation"},
    }

    async def run_evaluation(self, model_spec, benchmark_ids, config, progress_callback):
        """TTS evaluation pipeline:
        1. Synthesize test sentences with target model
        2. Score with UTMOS (naturalness)
        3. Score with WVMOS (complementary naturalness)
        4. Run STT on generated audio (intelligibility)
        5. Compare pronunciation against expected phonemes
        6. Analyze prosody features (pitch, rate)
        """
        ...
```

## Entry Point Registration

In `pyproject.toml`:

```toml
[project.entry-points."voicelearn_eval.plugins"]
lm_eval_harness = "voicelearn_eval.plugins.llm.lm_eval_harness:LMEvalHarnessPlugin"
stt_eval = "voicelearn_eval.plugins.stt.open_asr:STTEvalPlugin"
tts_eval = "voicelearn_eval.plugins.tts.quality:TTSEvalPlugin"
vad_eval = "voicelearn_eval.plugins.vad.vad_eval:VADEvalPlugin"
embeddings_eval = "voicelearn_eval.plugins.embeddings.mteb:EmbeddingsEvalPlugin"
```

## Adding a Custom Plugin

Third-party plugins can be created as separate Python packages:

```python
# my_custom_eval/plugin.py
from voicelearn_eval.plugins.base import BaseEvalPlugin, EvalPluginType, hookimpl

class MyCustomPlugin(BaseEvalPlugin):
    plugin_id = "my_custom"
    plugin_type = EvalPluginType.LLM

    @hookimpl
    def get_plugin_info(self):
        return EvalPluginMetadata(
            name="My Custom LLM Evaluator",
            plugin_id="my_custom",
            # ...
        )

    @hookimpl
    async def run_evaluation(self, model_spec, benchmark_ids, config, progress_callback):
        # Custom evaluation logic
        ...
```

```toml
# my_custom_eval/pyproject.toml
[project.entry-points."voicelearn_eval.plugins"]
my_custom = "my_custom_eval.plugin:MyCustomPlugin"
```

After `pip install my_custom_eval`, the plugin is automatically discovered.

## Plugin Isolation

Plugins that wrap GPU-heavy tools can run in subprocess mode for isolation:

```python
class SubprocessPluginRunner:
    """Runs a plugin in a separate process for GPU memory isolation."""

    async def run_isolated(self, plugin_id, model_spec, benchmarks, config):
        """Fork a subprocess, run the plugin, collect results via pipe."""
        cmd = [
            sys.executable, "-m", "voicelearn_eval.plugins.runner",
            "--plugin", plugin_id,
            "--model-spec", json.dumps(model_spec),
            "--benchmarks", json.dumps(benchmarks),
            "--config", json.dumps(config),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return json.loads(stdout)
```

This prevents GPU memory leaks from one evaluation affecting the next.
