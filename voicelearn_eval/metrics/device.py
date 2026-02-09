"""On-device performance metrics collection.

Measures CPU, memory, GPU (if available), and throughput during evaluation
to assess model suitability for different deployment targets.
"""

from __future__ import annotations

import os
import platform
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class DeviceSnapshot:
    """A point-in-time snapshot of device resource usage."""

    timestamp: float
    cpu_percent: float | None = None
    memory_rss_mb: float | None = None
    memory_percent: float | None = None
    gpu_memory_mb: float | None = None
    gpu_utilization_percent: float | None = None


@dataclass
class DeviceMetrics:
    """Aggregated device metrics from an evaluation run."""

    # CPU
    cpu_mean_percent: float | None = None
    cpu_peak_percent: float | None = None

    # Memory
    memory_mean_mb: float | None = None
    memory_peak_mb: float | None = None
    memory_mean_percent: float | None = None

    # GPU
    gpu_memory_mean_mb: float | None = None
    gpu_memory_peak_mb: float | None = None
    gpu_utilization_mean: float | None = None
    gpu_utilization_peak: float | None = None

    # Timing
    wall_time_seconds: float = 0.0
    samples_processed: int = 0
    throughput_samples_per_sec: float | None = None

    # Latency
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_p99_ms: float | None = None
    latency_mean_ms: float | None = None

    # System info
    platform_info: dict = field(default_factory=dict)

    snapshots: list[DeviceSnapshot] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "cpu_mean_percent": self.cpu_mean_percent,
            "cpu_peak_percent": self.cpu_peak_percent,
            "memory_mean_mb": self.memory_mean_mb,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_mean_percent": self.memory_mean_percent,
            "gpu_memory_mean_mb": self.gpu_memory_mean_mb,
            "gpu_memory_peak_mb": self.gpu_memory_peak_mb,
            "gpu_utilization_mean": self.gpu_utilization_mean,
            "gpu_utilization_peak": self.gpu_utilization_peak,
            "wall_time_seconds": self.wall_time_seconds,
            "samples_processed": self.samples_processed,
            "throughput_samples_per_sec": self.throughput_samples_per_sec,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "latency_mean_ms": self.latency_mean_ms,
            "platform_info": self.platform_info,
        }
        return {k: v for k, v in d.items() if v is not None}


def get_platform_info() -> dict:
    """Collect static system information."""
    info: dict = {
        "system": platform.system(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }

    try:
        import psutil

        mem = psutil.virtual_memory()
        info["total_memory_gb"] = round(mem.total / (1024**3), 2)
    except ImportError:
        pass

    # Check for GPU
    try:
        import torch

        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_memory_total_gb"] = round(
                torch.cuda.get_device_properties(0).total_mem / (1024**3), 2
            )
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            info["gpu_name"] = "Apple Silicon (MPS)"
            info["gpu_count"] = 1
    except ImportError:
        pass

    return info


def _take_snapshot() -> DeviceSnapshot:
    """Take a single resource snapshot."""
    snap = DeviceSnapshot(timestamp=time.monotonic())

    try:
        import psutil

        proc = psutil.Process()
        snap.cpu_percent = proc.cpu_percent(interval=None)
        mem_info = proc.memory_info()
        snap.memory_rss_mb = round(mem_info.rss / (1024**2), 2)
        snap.memory_percent = proc.memory_percent()
    except ImportError:
        pass

    try:
        import torch

        if torch.cuda.is_available():
            snap.gpu_memory_mb = round(
                torch.cuda.memory_allocated() / (1024**2), 2
            )
            # nvidia-smi based utilization requires pynvml
            try:
                import pynvml

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                snap.gpu_utilization_percent = util.gpu
            except (ImportError, Exception):
                pass
    except ImportError:
        pass

    return snap


def _percentile(values: list[float], p: float) -> float:
    """Calculate the p-th percentile of a list."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (p / 100.0) * (len(sorted_vals) - 1)
    lower = int(idx)
    upper = min(lower + 1, len(sorted_vals) - 1)
    frac = idx - lower
    return sorted_vals[lower] * (1 - frac) + sorted_vals[upper] * frac


def aggregate_snapshots(
    snapshots: list[DeviceSnapshot],
    wall_time: float,
    samples: int,
    latencies_ms: list[float] | None = None,
) -> DeviceMetrics:
    """Aggregate a list of snapshots into summary metrics."""
    metrics = DeviceMetrics(
        wall_time_seconds=round(wall_time, 3),
        samples_processed=samples,
        platform_info=get_platform_info(),
        snapshots=snapshots,
    )

    if samples > 0 and wall_time > 0:
        metrics.throughput_samples_per_sec = round(samples / wall_time, 2)

    cpu_vals = [s.cpu_percent for s in snapshots if s.cpu_percent is not None]
    if cpu_vals:
        metrics.cpu_mean_percent = round(sum(cpu_vals) / len(cpu_vals), 1)
        metrics.cpu_peak_percent = round(max(cpu_vals), 1)

    mem_vals = [s.memory_rss_mb for s in snapshots if s.memory_rss_mb is not None]
    if mem_vals:
        metrics.memory_mean_mb = round(sum(mem_vals) / len(mem_vals), 1)
        metrics.memory_peak_mb = round(max(mem_vals), 1)

    mem_pct = [s.memory_percent for s in snapshots if s.memory_percent is not None]
    if mem_pct:
        metrics.memory_mean_percent = round(sum(mem_pct) / len(mem_pct), 1)

    gpu_mem = [s.gpu_memory_mb for s in snapshots if s.gpu_memory_mb is not None]
    if gpu_mem:
        metrics.gpu_memory_mean_mb = round(sum(gpu_mem) / len(gpu_mem), 1)
        metrics.gpu_memory_peak_mb = round(max(gpu_mem), 1)

    gpu_util = [
        s.gpu_utilization_percent
        for s in snapshots
        if s.gpu_utilization_percent is not None
    ]
    if gpu_util:
        metrics.gpu_utilization_mean = round(sum(gpu_util) / len(gpu_util), 1)
        metrics.gpu_utilization_peak = round(max(gpu_util), 1)

    if latencies_ms:
        metrics.latency_mean_ms = round(sum(latencies_ms) / len(latencies_ms), 2)
        metrics.latency_p50_ms = round(_percentile(latencies_ms, 50), 2)
        metrics.latency_p95_ms = round(_percentile(latencies_ms, 95), 2)
        metrics.latency_p99_ms = round(_percentile(latencies_ms, 99), 2)

    return metrics


class MetricsCollector:
    """Collects device metrics during evaluation.

    Usage::

        collector = MetricsCollector(interval=1.0)
        with collector.session():
            for sample in data:
                with collector.measure_sample():
                    model(sample)
        metrics = collector.results()
    """

    def __init__(self, interval: float = 1.0):
        self._interval = interval
        self._snapshots: list[DeviceSnapshot] = []
        self._latencies: list[float] = []
        self._samples = 0
        self._start: float = 0
        self._end: float = 0
        self._last_snap: float = 0

    @contextmanager
    def session(self) -> Generator[None, None, None]:
        """Context manager for the overall collection session."""
        self._snapshots = []
        self._latencies = []
        self._samples = 0
        self._start = time.monotonic()
        self._last_snap = self._start

        # Initial snapshot
        try:
            import psutil  # noqa: F401

            psutil.Process().cpu_percent(interval=None)  # prime CPU measurement
        except ImportError:
            pass
        self._snapshots.append(_take_snapshot())

        try:
            yield
        finally:
            self._snapshots.append(_take_snapshot())
            self._end = time.monotonic()

    @contextmanager
    def measure_sample(self) -> Generator[None, None, None]:
        """Time a single sample / inference call."""
        t0 = time.monotonic()
        try:
            yield
        finally:
            t1 = time.monotonic()
            self._latencies.append((t1 - t0) * 1000)  # ms
            self._samples += 1

            # Periodic resource snapshot
            if t1 - self._last_snap >= self._interval:
                self._snapshots.append(_take_snapshot())
                self._last_snap = t1

    def results(self) -> DeviceMetrics:
        """Aggregate collected data into DeviceMetrics."""
        wall = self._end - self._start if self._end > self._start else 0
        return aggregate_snapshots(
            self._snapshots,
            wall,
            self._samples,
            self._latencies or None,
        )
