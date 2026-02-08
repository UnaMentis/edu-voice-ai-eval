"""Tests for grade-level scoring system."""


from voicelearn_eval.grade_levels.scorer import (
    assess_tier,
    calculate_overall_education_score,
    calculate_tier_score,
    compute_grade_level_rating,
    get_max_passing_tier,
)
from voicelearn_eval.grade_levels.tiers import DEFAULT_THRESHOLD


class TestCalculateTierScore:
    def test_basic_score(self):
        results = [
            {"education_tier": "elementary", "score": 80.0, "weight": 1.0, "task_name": "a"},
            {"education_tier": "elementary", "score": 90.0, "weight": 1.0, "task_name": "b"},
        ]
        score, breakdown = calculate_tier_score(results, "elementary")
        assert score == 85.0
        assert len(breakdown) == 2

    def test_weighted_score(self):
        results = [
            {"education_tier": "elementary", "score": 80.0, "weight": 2.0, "task_name": "a"},
            {"education_tier": "elementary", "score": 60.0, "weight": 1.0, "task_name": "b"},
        ]
        score, _ = calculate_tier_score(results, "elementary")
        expected = (80.0 * 2.0 + 60.0 * 1.0) / 3.0
        assert abs(score - expected) < 0.01

    def test_empty_tier(self):
        results = [
            {"education_tier": "highschool", "score": 80.0, "weight": 1.0, "task_name": "a"},
        ]
        score, breakdown = calculate_tier_score(results, "elementary")
        assert score == 0.0
        assert breakdown == []

    def test_none_scores_excluded(self):
        results = [
            {"education_tier": "elementary", "score": 80.0, "weight": 1.0, "task_name": "a"},
            {"education_tier": "elementary", "score": None, "weight": 1.0, "task_name": "b"},
        ]
        score, breakdown = calculate_tier_score(results, "elementary")
        assert score == 80.0
        assert len(breakdown) == 1


class TestAssessTier:
    def test_passing(self):
        assert assess_tier(75.0) is True

    def test_failing(self):
        assert assess_tier(65.0) is False

    def test_exact_threshold(self):
        assert assess_tier(DEFAULT_THRESHOLD) is True

    def test_custom_threshold(self):
        assert assess_tier(50.0, threshold=60.0) is False
        assert assess_tier(70.0, threshold=60.0) is True


class TestGetMaxPassingTier:
    def test_all_passing(self):
        scores = {
            "elementary": 90.0,
            "highschool": 85.0,
            "undergrad": 75.0,
            "grad": 72.0,
        }
        assert get_max_passing_tier(scores) == "grad"

    def test_sequential_pass_elementary_only(self):
        scores = {
            "elementary": 90.0,
            "highschool": 60.0,  # fails
            "undergrad": 80.0,
            "grad": 75.0,
        }
        # Even though undergrad/grad pass, highschool failed so max is elementary
        assert get_max_passing_tier(scores) == "elementary"

    def test_none_passing(self):
        scores = {"elementary": 50.0}
        assert get_max_passing_tier(scores) is None

    def test_empty_scores(self):
        assert get_max_passing_tier({}) is None


class TestOverallEducationScore:
    def test_weighted_average(self):
        scores = {
            "elementary": 100.0,
            "highschool": 80.0,
            "undergrad": 60.0,
            "grad": 40.0,
        }
        overall = calculate_overall_education_score(scores)
        # Elementary and HS have weight 1.0, Undergrad 0.8, Grad 0.6
        expected = (100 * 1.0 + 80 * 1.0 + 60 * 0.8 + 40 * 0.6) / (1.0 + 1.0 + 0.8 + 0.6)
        assert abs(overall - expected) < 0.01


class TestComputeGradeLevelRating:
    def test_full_computation(self):
        results = [
            {"education_tier": "elementary", "score": 85.0, "weight": 1.0, "task_name": "elem_math"},
            {"education_tier": "elementary", "score": 90.0, "weight": 1.0, "task_name": "elem_sci"},
            {"education_tier": "highschool", "score": 75.0, "weight": 1.0, "task_name": "hs_math"},
            {"education_tier": "undergrad", "score": 60.0, "weight": 1.0, "task_name": "ug_math"},
        ]
        rating = compute_grade_level_rating(
            model_id="m1", run_id="r1", task_results=results
        )
        assert rating.tier_scores["elementary"] == 87.5
        assert rating.tier_scores["highschool"] == 75.0
        assert rating.max_passing_tier == "highschool"  # undergrad < 70
        assert rating.overall_education_score > 0
        assert "elementary" in rating.tier_details
