"""Tests for the analyzer.regression module."""

from voicelearn_eval.analyzer.regression import (
    RegressionSeverity,
    ci_exit_code,
    detect_regressions,
)


class TestDetectRegressions:
    def test_no_regressions(self):
        baseline = [{"task_name": "math", "score": 70}]
        current = [{"task_name": "math", "score": 80}]
        result = detect_regressions(current, baseline)
        assert result["has_regression"] is False
        assert result["overall_severity"] == RegressionSeverity.NONE

    def test_minor_regression(self):
        baseline = [{"task_name": "math", "score": 80}]
        current = [{"task_name": "math", "score": 77}]  # ~3.75% decline
        result = detect_regressions(current, baseline)
        assert result["has_regression"] is True
        assert result["tasks"][0]["severity"] == RegressionSeverity.MINOR

    def test_critical_regression(self):
        """Dropping below the passing threshold is critical."""
        baseline = [{"task_name": "math", "score": 75}]
        current = [{"task_name": "math", "score": 65}]
        result = detect_regressions(current, baseline, threshold=70.0)
        assert result["has_regression"] is True
        assert result["tasks"][0]["severity"] == RegressionSeverity.CRITICAL

    def test_severe_regression(self):
        # Both scores above threshold so not critical, but >15% decline = severe
        baseline = [{"task_name": "math", "score": 90}]
        current = [{"task_name": "math", "score": 74}]  # ~17.8% decline, stays above 70
        result = detect_regressions(current, baseline)
        assert result["has_regression"] is True
        assert result["tasks"][0]["severity"] == RegressionSeverity.SEVERE

    def test_unmatched_tasks_ignored(self):
        baseline = [{"task_name": "math", "score": 80}]
        current = [{"task_name": "science", "score": 50}]
        result = detect_regressions(current, baseline)
        assert result["total_tasks_compared"] == 0
        assert result["has_regression"] is False


class TestCiExitCode:
    def test_clean(self):
        assert ci_exit_code({"overall_severity": RegressionSeverity.NONE}) == 0

    def test_minor(self):
        assert ci_exit_code({"overall_severity": RegressionSeverity.MINOR}) == 1

    def test_critical(self):
        assert ci_exit_code({"overall_severity": RegressionSeverity.CRITICAL}) == 2
