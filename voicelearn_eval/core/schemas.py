"""Pydantic schemas for API request/response validation."""


from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    name: str
    model_type: str  # llm, stt, tts, vad, embeddings
    source_type: str  # huggingface, local, api, ollama
    deployment_target: str = "server"
    source_uri: str | None = None
    source_format: str | None = None
    api_base_url: str | None = None
    api_key_env: str | None = None
    model_family: str | None = None
    model_version: str | None = None
    parameter_count_b: float | None = None
    model_size_gb: float | None = None
    quantization: str | None = None
    context_window: int | None = None
    education_tiers: list[str] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    is_reference: bool = False


class ModelUpdate(BaseModel):
    name: str | None = None
    deployment_target: str | None = None
    model_family: str | None = None
    model_version: str | None = None
    parameter_count_b: float | None = None
    model_size_gb: float | None = None
    quantization: str | None = None
    context_window: int | None = None
    education_tiers: list[str] | None = None
    subjects: list[str] | None = None
    languages: list[str] | None = None
    tags: list[str] | None = None
    notes: str | None = None
    is_reference: bool | None = None


class HuggingFaceImport(BaseModel):
    repo_id: str
    model_type: str
    deployment_target: str = "server"


class RunCreate(BaseModel):
    model_id: str
    suite_id: str
    config: dict | None = None
    priority: int = 5
    triggered_by: str = "manual"


class SuiteCreate(BaseModel):
    name: str
    model_type: str
    description: str | None = None
    category: str | None = None
    config: dict = Field(default_factory=dict)
    default_params: dict | None = None


class SuiteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    config: dict | None = None
    default_params: dict | None = None
    is_active: bool | None = None


class BaselineCreate(BaseModel):
    name: str
    description: str | None = None
    model_id: str
    run_id: str
    suite_id: str


class ShareCreate(BaseModel):
    report_type: str  # run, comparison, model_card
    report_config: dict
    expires_in_days: int | None = 30


class CustomTestSetCreate(BaseModel):
    name: str
    description: str | None = None
    model_type: str
    items: list[dict]
    tags: list[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    run_ids: list[str] | None = None
    model_id: str | None = None
    format: str = "vlef"  # vlef, json, csv
