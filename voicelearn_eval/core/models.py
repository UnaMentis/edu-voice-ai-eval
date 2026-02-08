"""Core data models for the evaluation system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ModelCategory(str, Enum):
    LLM = "llm"
    STT = "stt"
    TTS = "tts"
    VAD = "vad"
    EMBEDDINGS = "embeddings"


class DeploymentTarget(str, Enum):
    ON_DEVICE = "on-device"
    SERVER = "server"
    CLOUD_API = "cloud-api"


class EducationTier(str, Enum):
    ELEMENTARY = "elementary"       # Grades 5-8
    HIGH_SCHOOL = "highschool"      # Grades 9-12
    UNDERGRADUATE = "undergrad"     # College
    GRADUATE = "grad"               # Graduate/PhD


class RunStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ModelSpec:
    """Specification of a model to evaluate."""

    id: str
    name: str
    slug: str
    model_type: ModelCategory
    source_type: str  # "huggingface", "local", "api", "ollama"
    deployment_target: DeploymentTarget = DeploymentTarget.SERVER

    model_family: str | None = None
    model_version: str | None = None
    source_uri: str | None = None
    source_format: str | None = None
    api_base_url: str | None = None
    api_key_env: str | None = None

    parameter_count_b: float | None = None
    model_size_gb: float | None = None
    quantization: str | None = None
    context_window: int | None = None

    education_tiers: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    notes: str | None = None

    is_reference: bool = False
    is_active: bool = True
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "model_type": self.model_type.value if isinstance(self.model_type, Enum) else self.model_type,
            "source_type": self.source_type,
            "deployment_target": (
                self.deployment_target.value
                if isinstance(self.deployment_target, Enum)
                else self.deployment_target
            ),
            "model_family": self.model_family,
            "model_version": self.model_version,
            "source_uri": self.source_uri,
            "source_format": self.source_format,
            "api_base_url": self.api_base_url,
            "api_key_env": self.api_key_env,
            "parameter_count_b": self.parameter_count_b,
            "model_size_gb": self.model_size_gb,
            "quantization": self.quantization,
            "context_window": self.context_window,
            "education_tiers": self.education_tiers,
            "subjects": self.subjects,
            "languages": self.languages,
            "tags": self.tags,
            "notes": self.notes,
            "is_reference": self.is_reference,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelSpec":
        d = dict(data)
        if "model_type" in d and isinstance(d["model_type"], str):
            d["model_type"] = ModelCategory(d["model_type"])
        if "deployment_target" in d and isinstance(d["deployment_target"], str):
            d["deployment_target"] = DeploymentTarget(d["deployment_target"])
        for list_field in ("education_tiers", "subjects", "languages", "tags"):
            if list_field in d and isinstance(d[list_field], str):
                import json
                d[list_field] = json.loads(d[list_field]) if d[list_field] else []
        # Filter to only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**d)


@dataclass
class BenchmarkTask:
    """A single evaluation task within a suite."""

    id: str
    suite_id: str
    name: str
    task_type: str
    config: dict = field(default_factory=dict)
    description: str | None = None
    weight: float = 1.0
    education_tier: str | None = None
    subject: str | None = None
    order_index: int = 0
    created_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "suite_id": self.suite_id,
            "name": self.name,
            "task_type": self.task_type,
            "config": self.config,
            "description": self.description,
            "weight": self.weight,
            "education_tier": self.education_tier,
            "subject": self.subject,
            "order_index": self.order_index,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BenchmarkTask":
        import json

        d = dict(data)
        if "config" in d and isinstance(d["config"], str):
            d["config"] = json.loads(d["config"]) if d["config"] else {}
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**d)


@dataclass
class BenchmarkSuite:
    """Collection of evaluation tasks."""

    id: str
    name: str
    slug: str
    model_type: str
    config: dict = field(default_factory=dict)
    tasks: list[BenchmarkTask] = field(default_factory=list)
    description: str | None = None
    category: str | None = None
    default_params: dict | None = None
    is_builtin: bool = False
    is_active: bool = True
    created_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "model_type": self.model_type.value if isinstance(self.model_type, Enum) else self.model_type,
            "config": self.config,
            "description": self.description,
            "category": self.category,
            "default_params": self.default_params,
            "is_builtin": self.is_builtin,
            "is_active": self.is_active,
            "task_count": len(self.tasks),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BenchmarkSuite":
        import json

        d = dict(data)
        for json_field in ("config", "default_params"):
            if json_field in d and isinstance(d[json_field], str):
                d[json_field] = json.loads(d[json_field]) if d[json_field] else {}
        # Handle tasks separately
        tasks_data = d.pop("tasks", [])
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        suite = cls(**d)
        if tasks_data and isinstance(tasks_data[0], dict):
            suite.tasks = [BenchmarkTask.from_dict(t) for t in tasks_data]
        return suite


@dataclass
class EvalTaskResult:
    """Result from a single benchmark task."""

    id: str
    run_id: str
    task_id: str
    score: float | None = None  # 0-100 normalized
    raw_score: float | None = None
    raw_metric_name: str | None = None
    metrics: dict = field(default_factory=dict)
    latency_ms: float | None = None
    throughput: float | None = None
    memory_peak_mb: float | None = None
    gpu_memory_peak_mb: float | None = None
    sample_audio_path: str | None = None
    sample_text: str | None = None
    status: str = "completed"
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None
    created_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "score": self.score,
            "raw_score": self.raw_score,
            "raw_metric_name": self.raw_metric_name,
            "metrics": self.metrics,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
            "memory_peak_mb": self.memory_peak_mb,
            "gpu_memory_peak_mb": self.gpu_memory_peak_mb,
            "sample_audio_path": self.sample_audio_path,
            "sample_text": self.sample_text,
            "status": self.status,
            "error_message": self.error_message,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvalTaskResult":
        import json

        d = dict(data)
        if "metrics" in d and isinstance(d["metrics"], str):
            d["metrics"] = json.loads(d["metrics"]) if d["metrics"] else {}
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**d)


@dataclass
class EvalRun:
    """A complete evaluation run."""

    id: str
    model_id: str
    suite_id: str
    status: RunStatus = RunStatus.PENDING
    progress_percent: float = 0
    current_task: str | None = None
    tasks_completed: int = 0
    tasks_total: int = 0
    overall_score: float | None = None
    overall_metrics: dict | None = None
    run_config: dict | None = None
    run_params: dict | None = None
    hardware_info: dict | None = None
    software_info: dict | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    triggered_by: str = "manual"
    schedule_id: str | None = None
    run_version: int = 1
    queued_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    results: list[EvalTaskResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "model_id": self.model_id,
            "suite_id": self.suite_id,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "progress_percent": self.progress_percent,
            "current_task": self.current_task,
            "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total,
            "overall_score": self.overall_score,
            "overall_metrics": self.overall_metrics,
            "run_config": self.run_config,
            "run_params": self.run_params,
            "hardware_info": self.hardware_info,
            "software_info": self.software_info,
            "error_message": self.error_message,
            "triggered_by": self.triggered_by,
            "run_version": self.run_version,
            "queued_at": self.queued_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvalRun":
        import json

        d = dict(data)
        if "status" in d and isinstance(d["status"], str):
            d["status"] = RunStatus(d["status"])
        for json_field in ("overall_metrics", "run_config", "run_params", "hardware_info", "software_info"):
            if json_field in d and isinstance(d[json_field], str):
                d[json_field] = json.loads(d[json_field]) if d[json_field] else None
        results_data = d.pop("results", [])
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        run = cls(**d)
        if results_data and isinstance(results_data[0], dict):
            run.results = [EvalTaskResult.from_dict(r) for r in results_data]
        return run


@dataclass
class GradeLevelRating:
    """Grade-level capability assessment for a model."""

    model_id: str
    run_id: str
    tier_scores: dict[str, float] = field(default_factory=dict)
    max_passing_tier: str | None = None
    tier_details: dict[str, list[dict]] = field(default_factory=dict)
    threshold: float = 70.0
    overall_education_score: float | None = None

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "run_id": self.run_id,
            "tier_scores": self.tier_scores,
            "max_passing_tier": self.max_passing_tier,
            "tier_details": self.tier_details,
            "threshold": self.threshold,
            "overall_education_score": self.overall_education_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GradeLevelRating":
        d = dict(data)
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**d)


@dataclass
class VLEFExport:
    """Voice Learning Eval Format: portable evaluation results."""

    format_version: str = "1.0"
    exported_at: str | None = None
    runs: list[dict] = field(default_factory=list)
    models: list[dict] = field(default_factory=list)
    suites: list[dict] = field(default_factory=list)
    grade_level_ratings: list[dict] = field(default_factory=list)
    environment: dict = field(default_factory=dict)
    attribution: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "format_version": self.format_version,
            "exported_at": self.exported_at or datetime.utcnow().isoformat(),
            "runs": self.runs,
            "models": self.models,
            "suites": self.suites,
            "grade_level_ratings": self.grade_level_ratings,
            "environment": self.environment,
            "attribution": self.attribution,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VLEFExport":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**d)
