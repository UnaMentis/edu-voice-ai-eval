"""Tests for the analyzer.statistics module."""


from voicelearn_eval.analyzer.statistics import (
    aggregate_scores,
    percentile,
    score_by_category,
)


class TestAggregateScores:
    def test_basic_aggregation(self):
        results = [{"score": 80}, {"score": 90}, {"score": 70}]
        stats = aggregate_scores(results)
        assert stats["mean"] == 80.0
        assert stats["median"] == 80.0
        assert stats["min"] == 70.0
        assert stats["max"] == 90.0
        assert stats["count"] == 3
        assert stats["confidence_interval_95"] is not None

    def test_empty_results(self):
        stats = aggregate_scores([])
        assert stats["mean"] is None
        assert stats["count"] == 0

    def test_skips_none_scores(self):
        results = [{"score": 80}, {"score": None}, {"score": 60}]
        stats = aggregate_scores(results)
        assert stats["count"] == 2
        assert stats["mean"] == 70.0

    def test_single_score(self):
        stats = aggregate_scores([{"score": 50}])
        assert stats["mean"] == 50.0
        assert stats["median"] == 50.0
        assert stats["std_dev"] == 0.0

    def test_even_count_median(self):
        results = [{"score": 10}, {"score": 20}, {"score": 30}, {"score": 40}]
        stats = aggregate_scores(results)
        assert stats["median"] == 25.0


class TestScoreByCategory:
    def test_groups_by_tier(self):
        results = [
            {"score": 80, "education_tier": "elementary"},
            {"score": 90, "education_tier": "elementary"},
            {"score": 60, "education_tier": "graduate"},
        ]
        grouped = score_by_category(results, "education_tier")
        assert "elementary" in grouped
        assert "graduate" in grouped
        assert grouped["elementary"]["mean"] == 85.0
        assert grouped["graduate"]["mean"] == 60.0

    def test_missing_category_key(self):
        results = [{"score": 50}]
        grouped = score_by_category(results, "education_tier")
        assert "unknown" in grouped


class TestPercentile:
    def test_median(self):
        assert percentile([10, 20, 30, 40, 50], 50) == 30

    def test_percentile_0(self):
        assert percentile([10, 20, 30], 0) == 10

    def test_percentile_100(self):
        assert percentile([10, 20, 30], 100) == 30

    def test_empty_list(self):
        assert percentile([], 50) == 0.0
