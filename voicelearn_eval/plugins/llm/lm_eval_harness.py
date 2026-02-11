"""LLM evaluation plugin wrapping EleutherAI lm-evaluation-harness."""

import logging
from collections.abc import Callable

from voicelearn_eval.grade_levels.mmlu_mapping import BENCHMARK_TO_LM_EVAL
from voicelearn_eval.plugins.base import (
    BaseEvalPlugin,
    EvalPluginMetadata,
    EvalPluginType,
    hookimpl,
)

logger = logging.getLogger(__name__)

try:
    import lm_eval

    LM_EVAL_AVAILABLE = True
except ImportError:
    LM_EVAL_AVAILABLE = False


class LMEvalHarnessPlugin(BaseEvalPlugin):
    """LLM evaluation via EleutherAI lm-evaluation-harness."""

    plugin_id = "lm_eval_harness"
    plugin_type = EvalPluginType.LLM

    @hookimpl
    def get_plugin_info(self) -> EvalPluginMetadata:
        return EvalPluginMetadata(
            name="EleutherAI lm-evaluation-harness",
            plugin_id=self.plugin_id,
            version="0.1.0",
            description="LLM evaluation using lm-evaluation-harness with education-tier mapping",
            plugin_type=self.plugin_type,
            upstream_project="EleutherAI lm-evaluation-harness",
            upstream_url="https://github.com/EleutherAI/lm-evaluation-harness",
            upstream_license="MIT",
            supported_benchmarks=list(BENCHMARK_TO_LM_EVAL.keys()),
            requires_gpu=True,
        )

    @hookimpl
    def get_supported_benchmarks(self) -> list[dict]:
        from voicelearn_eval.grade_levels.mmlu_mapping import TASK_SUBJECTS

        benchmarks = []
        for task_name, lm_eval_tasks in BENCHMARK_TO_LM_EVAL.items():
            benchmarks.append(
                {
                    "id": task_name,
                    "name": task_name.replace("_", " ").title(),
                    "description": f"lm-eval tasks: {', '.join(lm_eval_tasks)}",
                    "plugin_id": self.plugin_id,
                    "subject": TASK_SUBJECTS.get(task_name, "general"),
                    "lm_eval_tasks": lm_eval_tasks,
                }
            )
        return benchmarks

    @hookimpl
    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        model_type = model_spec.get("model_type", "")
        if model_type != "llm":
            return False, f"This plugin evaluates LLMs, got model_type={model_type}"

        source_type = model_spec.get("source_type", "")
        if source_type not in ("huggingface", "local", "api", "ollama"):
            return False, f"Unsupported source_type: {source_type}"

        return True, "OK"

    @hookimpl
    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run LLM evaluation.

        If lm-eval is installed, uses its Python API.
        Otherwise returns mock results for development/testing.
        """
        if not LM_EVAL_AVAILABLE:
            logger.warning(
                "lm-eval not installed. Returning mock results. "
                "Install with: pip install edu-voice-ai-eval[llm]"
            )
            return await self._mock_evaluation(
                model_spec, benchmark_ids, config, progress_callback
            )

        return await self._real_evaluation(
            model_spec, benchmark_ids, config, progress_callback
        )

    async def _real_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run actual lm-eval evaluation."""
        results = []
        model_type, model_args = self._determine_model_args(model_spec)

        # Collect all lm-eval tasks
        all_tasks = []
        task_to_benchmark = {}
        for bench_id in benchmark_ids:
            lm_tasks = BENCHMARK_TO_LM_EVAL.get(bench_id, [])
            for task in lm_tasks:
                all_tasks.append(task)
                task_to_benchmark[task] = bench_id

        if not all_tasks:
            return results

        try:
            # Run lm-eval
            eval_results = lm_eval.simple_evaluate(
                model=model_type,
                model_args=model_args,
                tasks=all_tasks,
                batch_size=config.get("batch_size", 8),
                device=config.get("gpu_device", "auto"),
                num_fewshot=config.get("num_fewshot"),
            )

            # Parse results
            raw_results = eval_results.get("results", {})
            for task_name, task_data in raw_results.items():
                bench_id = task_to_benchmark.get(task_name, task_name)

                # Extract primary metric
                raw_score = self._extract_primary_metric(task_data)
                metric_name = self._get_primary_metric_name(task_data)
                score = self.normalize_score(raw_score, metric_name)

                results.append(
                    self.make_result(
                        task_id=bench_id,
                        score=score,
                        raw_score=raw_score,
                        raw_metric_name=metric_name,
                        metrics=dict(task_data),
                    )
                )

        except Exception as e:
            logger.error(f"lm-eval failed: {e}")
            for bench_id in benchmark_ids:
                results.append(
                    self.make_result(
                        task_id=bench_id,
                        score=0,
                        raw_score=0,
                        raw_metric_name="error",
                        status="failed",
                        error_message=str(e),
                    )
                )

        return results

    async def _mock_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Return mock results when lm-eval is not installed."""
        import asyncio
        import random

        results = []
        for i, bench_id in enumerate(benchmark_ids):
            if progress_callback:
                await progress_callback(
                    bench_id, i, len(benchmark_ids), "Running (mock)..."
                )

            # Simulate some work
            await asyncio.sleep(0.1)

            # Generate plausible mock scores based on tier
            mock_scores = {
                "elementary": random.uniform(70, 95),
                "highschool": random.uniform(55, 85),
                "undergrad": random.uniform(35, 70),
                "grad": random.uniform(20, 55),
            }

            # Determine tier from benchmark config
            tier = config.get("education_tier", "highschool")
            base_score = mock_scores.get(tier, random.uniform(40, 80))
            score = min(100, max(0, base_score + random.uniform(-5, 5)))
            raw_score = score / 100.0

            results.append(
                self.make_result(
                    task_id=bench_id,
                    score=round(score, 1),
                    raw_score=round(raw_score, 4),
                    raw_metric_name="accuracy",
                    metrics={
                        "accuracy": raw_score,
                        "mock": True,
                        "note": "lm-eval not installed; install with pip install edu-voice-ai-eval[llm]",
                    },
                )
            )

        return results

    def _determine_model_args(self, model_spec: dict) -> tuple[str, str]:
        """Map our model spec to lm-eval model type and args."""
        source_type = model_spec.get("source_type", "huggingface")
        source_uri = model_spec.get("source_uri", "")

        if source_type == "huggingface":
            model_type = "hf"
            path = model_spec.get("local_path") or source_uri
            args = f"pretrained={path}"
            if model_spec.get("quantization"):
                args += ",dtype=float16"
            return model_type, args

        elif source_type == "local":
            fmt = model_spec.get("source_format", "")
            if fmt == "gguf":
                return "hf", f"pretrained={source_uri}"
            return "hf", f"pretrained={source_uri}"

        elif source_type == "api":
            base_url = model_spec.get("api_base_url", "")
            return "local-completions", f"model={source_uri},base_url={base_url}"

        elif source_type == "ollama":
            return (
                "local-completions",
                f"model={source_uri},base_url=http://localhost:11434/v1",
            )

        return "hf", f"pretrained={source_uri}"

    @staticmethod
    def _extract_primary_metric(task_data: dict) -> float:
        """Extract the primary metric from lm-eval task results."""
        for key in ("acc_norm,none", "acc,none", "exact_match,none", "f1,none", "acc_norm", "acc", "exact_match"):
            if key in task_data:
                val = task_data[key]
                return val if isinstance(val, (int, float)) else 0.0
        return 0.0

    @staticmethod
    def _get_primary_metric_name(task_data: dict) -> str:
        """Determine primary metric name from lm-eval task results."""
        for key in ("acc_norm,none", "acc,none", "exact_match,none", "f1,none"):
            if key in task_data:
                return key.split(",")[0]
        return "accuracy"
