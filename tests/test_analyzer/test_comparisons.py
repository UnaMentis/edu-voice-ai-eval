"""Tests for the analyzer.comparisons module."""

from voicelearn_eval.analyzer.comparisons import (
    build_radar_data,
    compare_model_results,
)


def _make_model_results(name, model_id, scores, tier="elementary", is_ref=False):
    return {
        "model": {"id": model_id, "name": name, "model_type": "llm", "is_reference": is_ref},
        "run": {"id": f"run-{model_id}", "overall_score": sum(scores) / len(scores) if scores else 0},
        "results": [
            {"score": s, "education_tier": tier, "task_name": f"task_{i}"}
            for i, s in enumerate(scores)
        ],
    }


class TestCompareModelResults:
    def test_basic_comparison(self):
        mr = [
            _make_model_results("A", "a", [80, 90]),
            _make_model_results("B", "b", [60, 70]),
        ]
        result = compare_model_results(mr)
        assert result["summary"]["model_count"] == 2
        assert result["summary"]["best_model"] == "A"
        assert len(result["models"]) == 2

    def test_delta_from_reference(self):
        mr = [
            _make_model_results("Ref", "ref", [70], is_ref=True),
            _make_model_results("Test", "test", [80]),
        ]
        result = compare_model_results(mr)
        assert result["reference_model_id"] == "ref"
        test_entry = next(m for m in result["models"] if m["model_id"] == "test")
        assert "delta_from_reference" in test_entry
        assert test_entry["delta_from_reference"] > 0


class TestBuildRadarData:
    def test_radar_dimensions(self):
        mr = [
            _make_model_results("A", "a", [80, 90], tier="elementary"),
        ]
        data = build_radar_data(mr, ["elementary"])
        assert len(data) == 1
        assert data[0]["model_name"] == "A"
        assert len(data[0]["values"]) == 1
        assert data[0]["values"][0] == 85.0
