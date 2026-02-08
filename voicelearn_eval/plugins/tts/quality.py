"""TTS evaluation plugin for quality assessment."""

import logging
from collections.abc import Callable

from voicelearn_eval.plugins.base import (
    BaseEvalPlugin,
    EvalPluginMetadata,
    EvalPluginType,
)

logger = logging.getLogger(__name__)


class TTSEvalPlugin(BaseEvalPlugin):
    """Evaluate text-to-speech models on MOS, intelligibility, pronunciation, prosody."""

    plugin_id = "tts_eval"
    plugin_type = EvalPluginType.TTS

    def get_plugin_info(self) -> EvalPluginMetadata:
        return EvalPluginMetadata(
            name="TTS Evaluation Plugin",
            plugin_id=self.plugin_id,
            version="0.1.0",
            description="Text-to-speech quality evaluation with MOS, intelligibility, and pronunciation",
            plugin_type=EvalPluginType.TTS,
            upstream_project="UTMOS + WVMOS",
            supported_benchmarks=[
                "mos_standard",
                "intelligibility",
                "pronunciation_science",
                "pronunciation_math",
                "prosody",
            ],
        )

    def get_supported_benchmarks(self) -> list[dict]:
        return [
            {"id": "mos_standard", "name": "MOS Standard", "metric": "mos"},
            {"id": "intelligibility", "name": "Intelligibility", "metric": "wer"},
            {"id": "pronunciation_science", "name": "Pronunciation - Science", "metric": "per"},
            {"id": "pronunciation_math", "name": "Pronunciation - Math", "metric": "per"},
            {"id": "prosody", "name": "Prosody", "metric": "prosody_score"},
        ]

    def validate_model(self, model_spec: dict) -> tuple[bool, str]:
        if model_spec.get("model_type") != "tts":
            return False, "Not a TTS model"
        return True, "OK"

    async def run_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Run TTS evaluation. Returns mock results when dependencies unavailable."""
        try:
            return await self._run_real_evaluation(model_spec, benchmark_ids, config, progress_callback)
        except ImportError as e:
            logger.warning(f"TTS dependencies not available ({e}), returning mock results")
            return await self._run_mock_evaluation(benchmark_ids, progress_callback)

    async def _run_real_evaluation(
        self,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Real evaluation using UTMOS/WVMOS + Whisper round-trip."""
        # TODO: Implement real TTS evaluation pipeline
        # 1. Generate speech samples from test sentences
        # 2. Score with UTMOS/WVMOS for MOS
        # 3. Whisper round-trip for intelligibility WER
        # 4. Montreal Forced Aligner for pronunciation accuracy
        # 5. Pitch/rate analysis for prosody
        raise ImportError("Full TTS evaluation not yet implemented")

    async def _run_mock_evaluation(
        self,
        benchmark_ids: list[str],
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Return mock results for testing the pipeline."""
        import random

        results = []
        mock_scores = {
            "mos_standard": {"raw": 3.8, "metric": "mos"},
            "intelligibility": {"raw": 0.06, "metric": "wer"},
            "pronunciation_science": {"raw": 0.08, "metric": "per"},
            "pronunciation_math": {"raw": 0.12, "metric": "per"},
            "prosody": {"raw": 72.0, "metric": "prosody_score"},
        }

        for i, bid in enumerate(benchmark_ids):
            if progress_callback:
                await progress_callback(bid, i, len(benchmark_ids), f"Mock TTS eval: {bid}")

            info = mock_scores.get(bid, {"raw": 0.5, "metric": "accuracy"})
            raw = info["raw"] + random.uniform(-0.1, 0.1)
            metric = info["metric"]
            score = self.normalize_score(raw, metric)

            results.append(self.make_result(
                task_id=bid,
                score=round(score, 1),
                raw_score=round(raw, 4),
                raw_metric_name=metric,
                metrics={metric: raw, "mock": True},
            ))

        return results
