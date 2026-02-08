"""Tests for core data models."""

from voicelearn_eval.core.models import (
    BenchmarkTask,
    EducationTier,
    GradeLevelRating,
    ModelCategory,
    ModelSpec,
    RunStatus,
    VLEFExport,
)


class TestEnums:
    def test_model_category_values(self):
        assert ModelCategory.LLM.value == "llm"
        assert ModelCategory.STT.value == "stt"
        assert ModelCategory.TTS.value == "tts"

    def test_education_tier_values(self):
        assert EducationTier.ELEMENTARY.value == "elementary"
        assert EducationTier.HIGH_SCHOOL.value == "highschool"
        assert EducationTier.UNDERGRADUATE.value == "undergrad"
        assert EducationTier.GRADUATE.value == "grad"

    def test_run_status_values(self):
        assert RunStatus.PENDING.value == "pending"
        assert RunStatus.COMPLETED.value == "completed"
        assert RunStatus.FAILED.value == "failed"


class TestModelSpec:
    def test_to_dict_and_back(self):
        spec = ModelSpec(
            id="test-id",
            name="Test Model",
            slug="test-model",
            model_type=ModelCategory.LLM,
            source_type="huggingface",
            parameter_count_b=7.0,
        )
        d = spec.to_dict()
        assert d["model_type"] == "llm"
        assert d["parameter_count_b"] == 7.0

        restored = ModelSpec.from_dict(d)
        assert restored.name == "Test Model"
        assert restored.model_type == ModelCategory.LLM

    def test_from_dict_ignores_unknown_fields(self):
        data = {
            "id": "x",
            "name": "X",
            "slug": "x",
            "model_type": "llm",
            "source_type": "local",
            "unknown_field": "ignored",
        }
        spec = ModelSpec.from_dict(data)
        assert spec.name == "X"


class TestBenchmarkTask:
    def test_roundtrip(self):
        task = BenchmarkTask(
            id="t1",
            suite_id="s1",
            name="MMLU Elementary",
            task_type="llm",
            education_tier="elementary",
            weight=1.0,
        )
        d = task.to_dict()
        restored = BenchmarkTask.from_dict(d)
        assert restored.education_tier == "elementary"
        assert restored.weight == 1.0


class TestGradeLevelRating:
    def test_roundtrip(self):
        rating = GradeLevelRating(
            model_id="m1",
            run_id="r1",
            tier_scores={"elementary": 85.0, "highschool": 72.0},
            max_passing_tier="highschool",
            overall_education_score=78.5,
        )
        d = rating.to_dict()
        assert d["max_passing_tier"] == "highschool"

        restored = GradeLevelRating.from_dict(d)
        assert restored.tier_scores["elementary"] == 85.0


class TestVLEFExport:
    def test_to_dict(self):
        export = VLEFExport(
            format_version="1.0",
            runs=[{"id": "r1"}],
            models=[{"id": "m1"}],
        )
        d = export.to_dict()
        assert d["format_version"] == "1.0"
        assert len(d["runs"]) == 1
        assert "exported_at" in d
