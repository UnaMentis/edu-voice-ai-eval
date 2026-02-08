"""STT evaluation plugin using Open ASR benchmarks."""

import logging
from collections.abc import Callable

from voicelearn_eval.plugins.base import (
    BaseEvalPlugin,
    EvalPluginMetadata,
    EvalPluginType,
)

logger = logging.getLogger(__name__)


class STTEvalPlugin(BaseEvalPlugin):
    """Evaluate speech-to-text models on WER/CER benchmarks."""

    plugin_id = "stt_eval"
    plugin_type = EvalPluginType.STT

    def get_plugin_info(self) -> EvalPluginMetadata:
        return EvalPluginMetadata(
            name="STT Evaluation Plugin",
            plugin_id=self.plugin_id,
            version="0.1.0",
            description="Speech-to-text evaluation using WER/CER metrics",
            plugin_type=EvalPluginType.STT,
            upstream_project="jiwer + transformers",
            supported_benchmarks=[
                "librispeech_clean",
                "librispeech_other",
                "common_voice_en",
                "tedlium",
                "edu_tier1",
                "edu_tier2",
                "edu_tier3",
                "edu_tier4",
            ],
        )

    def get_supported_benchmarks(self) -> list[dict]:
        return [
            {"id": "librispeech_clean", "name": "LibriSpeech Clean", "metric": "wer"},
            {"id": "librispeech_other", "name": "LibriSpeech Other", "metric": "wer"},
            {"id": "common_voice_en", "name": "Common Voice EN", "metric": "wer"},
            {"id": "tedlium", "name": "TED-LIUM", "metric": "wer"},
            {"id": "edu_tier1", "name": "Edu Vocabulary Tier 1", "metric": "wer"},
            {"id": "edu_tier2", "name": "Edu Vocabulary Tier 2", "metric": "wer"},
            {"id": "edu_tier3", "name": "Edu Vocabulary Tier 3", "metric": "wer"},
            {"id": "edu_tier4", "name": "Edu Vocabulary Tier 4", "metric": "wer"},
        ]

    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        if model_spec.get("model_type") != "stt":
            return False, "Not an STT model"
        return True, "OK"

    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run STT evaluation. Returns mock results when dependencies unavailable."""
        try:
            return await self._run_real_evaluation(model_spec, benchmark_ids, config, progress_callback)
        except ImportError as e:
            logger.warning(f"STT dependencies not available ({e}), returning mock results")
            return await self._run_mock_evaluation(benchmark_ids, progress_callback)

    async def _run_real_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Real evaluation using transformers + jiwer."""
        import jiwer  # noqa: F401
        from transformers import pipeline  # noqa: F401

        # TODO: Implement real STT evaluation pipeline
        # 1. Load model via transformers pipeline
        # 2. Run inference on benchmark audio
        # 3. Calculate WER/CER using jiwer
        raise ImportError("Full STT evaluation not yet implemented")

    async def _run_mock_evaluation(
        self,
        benchmark_ids: list[str],
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Return mock results for testing the pipeline."""
        import random

        results = []
        mock_wer = {
            "librispeech_clean": 0.035,
            "librispeech_other": 0.078,
            "common_voice_en": 0.092,
            "tedlium": 0.065,
            "edu_tier1": 0.045,
            "edu_tier2": 0.068,
            "edu_tier3": 0.095,
            "edu_tier4": 0.125,
        }

        for i, bid in enumerate(benchmark_ids):
            if progress_callback:
                await progress_callback(bid, i, len(benchmark_ids), f"Mock STT eval: {bid}")

            wer = mock_wer.get(bid, 0.08) + random.uniform(-0.01, 0.01)
            wer = max(0.0, min(1.0, wer))
            score = self.normalize_score(wer, "wer")

            results.append(self.make_result(
                task_id=bid,
                score=round(score, 1),
                raw_score=round(wer, 4),
                raw_metric_name="wer",
                metrics={"wer": wer, "mock": True},
            ))

        return results
