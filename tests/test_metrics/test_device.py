"""Tests for the metrics.device module."""

import time

from voicelearn_eval.metrics.device import (
    DeviceMetrics,
    DeviceSnapshot,
    MetricsCollector,
    aggregate_snapshots,
    get_platform_info,
)


class TestGetPlatformInfo:
    def test_returns_basic_info(self):
        info = get_platform_info()
        assert "system" in info
        assert "machine" in info
        assert "python_version" in info
        assert "cpu_count" in info
        assert isinstance(info["cpu_count"], int)


class TestAggregateSnapshots:
    def test_empty_snapshots(self):
        metrics = aggregate_snapshots([], wall_time=1.0, samples=0)
        assert metrics.wall_time_seconds == 1.0
        assert metrics.samples_processed == 0
        assert metrics.throughput_samples_per_sec is None

    def test_with_cpu_snapshots(self):
        snaps = [
            DeviceSnapshot(timestamp=0.0, cpu_percent=50.0, memory_rss_mb=100.0),
            DeviceSnapshot(timestamp=1.0, cpu_percent=80.0, memory_rss_mb=120.0),
            DeviceSnapshot(timestamp=2.0, cpu_percent=60.0, memory_rss_mb=110.0),
        ]
        metrics = aggregate_snapshots(snaps, wall_time=2.0, samples=10)
        assert metrics.cpu_mean_percent is not None
        assert 60.0 <= metrics.cpu_mean_percent <= 64.0  # ~63.3
        assert metrics.cpu_peak_percent == 80.0
        assert metrics.memory_peak_mb == 120.0
        assert metrics.throughput_samples_per_sec == 5.0

    def test_with_latencies(self):
        snaps = [DeviceSnapshot(timestamp=0.0)]
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
        metrics = aggregate_snapshots(
            snaps, wall_time=1.0, samples=5, latencies_ms=latencies
        )
        assert metrics.latency_mean_ms == 30.0
        assert metrics.latency_p50_ms == 30.0
        assert metrics.latency_p95_ms is not None
        assert metrics.latency_p99_ms is not None

    def test_gpu_metrics(self):
        snaps = [
            DeviceSnapshot(timestamp=0.0, gpu_memory_mb=500.0, gpu_utilization_percent=70.0),
            DeviceSnapshot(timestamp=1.0, gpu_memory_mb=800.0, gpu_utilization_percent=90.0),
        ]
        metrics = aggregate_snapshots(snaps, wall_time=1.0, samples=1)
        assert metrics.gpu_memory_peak_mb == 800.0
        assert metrics.gpu_memory_mean_mb == 650.0
        assert metrics.gpu_utilization_peak == 90.0


class TestDeviceMetrics:
    def test_to_dict_omits_none(self):
        m = DeviceMetrics(wall_time_seconds=2.5, samples_processed=100)
        d = m.to_dict()
        assert d["wall_time_seconds"] == 2.5
        assert d["samples_processed"] == 100
        assert "cpu_mean_percent" not in d  # None fields excluded
        assert "gpu_memory_peak_mb" not in d


class TestMetricsCollector:
    def test_basic_session(self):
        collector = MetricsCollector(interval=0.5)
        with collector.session():
            for _ in range(3):
                with collector.measure_sample():
                    time.sleep(0.01)

        results = collector.results()
        assert results.samples_processed == 3
        assert results.wall_time_seconds > 0
        assert results.latency_mean_ms is not None
        assert results.latency_mean_ms >= 5  # at least 5ms each
        assert len(results.snapshots) >= 2  # start + end at minimum

    def test_throughput_calculated(self):
        collector = MetricsCollector(interval=10.0)  # won't trigger mid-session
        with collector.session():
            for _ in range(5):
                with collector.measure_sample():
                    time.sleep(0.001)

        results = collector.results()
        assert results.throughput_samples_per_sec is not None
        assert results.throughput_samples_per_sec > 0
