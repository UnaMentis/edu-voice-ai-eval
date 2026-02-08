"""Tests for plugin system."""


from voicelearn_eval.plugins.base import (
    BaseEvalPlugin,
    PluginRegistry,
)


class TestNormalizeScore:
    def test_accuracy_0_to_1(self):
        assert BaseEvalPlugin.normalize_score(0.85, "accuracy") == 85.0

    def test_accuracy_already_percent(self):
        assert BaseEvalPlugin.normalize_score(85.0, "accuracy") == 85.0

    def test_wer_inverted(self):
        assert BaseEvalPlugin.normalize_score(0.15, "wer") == 85.0

    def test_mos_scaling(self):
        # MOS 5.0 -> 100, MOS 1.0 -> 0
        assert BaseEvalPlugin.normalize_score(5.0, "mos") == 100.0
        assert BaseEvalPlugin.normalize_score(1.0, "mos") == 0.0
        assert BaseEvalPlugin.normalize_score(3.0, "mos") == 50.0

    def test_per_inverted(self):
        assert BaseEvalPlugin.normalize_score(0.1, "per") == 90.0


class TestMakeResult:
    def test_basic_result(self):
        result = BaseEvalPlugin.make_result(
            task_id="t1",
            score=85.0,
            raw_score=0.85,
            raw_metric_name="accuracy",
        )
        assert result["task_id"] == "t1"
        assert result["score"] == 85.0
        assert result["status"] == "completed"

    def test_extra_kwargs(self):
        result = BaseEvalPlugin.make_result(
            task_id="t1",
            score=85.0,
            raw_score=0.85,
            raw_metric_name="accuracy",
            latency_ms=150.0,
        )
        assert result["latency_ms"] == 150.0


class TestPluginRegistry:
    def test_register_and_get(self, mock_plugin):
        registry = PluginRegistry()
        registry.register(mock_plugin)
        assert registry.get_plugin("mock_llm") is mock_plugin

    def test_get_plugins_for_type(self, plugin_registry):
        plugins = plugin_registry.get_plugins_for_type("llm")
        assert len(plugins) == 1
        assert plugins[0].plugin_id == "mock_llm"

    def test_get_all_benchmarks(self, plugin_registry):
        benchmarks = plugin_registry.get_all_benchmarks()
        assert len(benchmarks) == 3
        ids = [b["id"] for b in benchmarks]
        assert "mmlu" in ids

    def test_find_plugin_for_benchmark(self, plugin_registry):
        plugin = plugin_registry.find_plugin_for_benchmark("mmlu")
        assert plugin is not None
        assert plugin.plugin_id == "mock_llm"

    def test_find_plugin_not_found(self, plugin_registry):
        plugin = plugin_registry.find_plugin_for_benchmark("nonexistent")
        assert plugin is None

    def test_find_plugin_for_model_type(self, plugin_registry):
        plugin = plugin_registry.find_plugin_for_model_type("llm")
        assert plugin is not None

        plugin = plugin_registry.find_plugin_for_model_type("stt")
        assert plugin is None
