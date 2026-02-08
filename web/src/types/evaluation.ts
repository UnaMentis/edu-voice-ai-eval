// ──────────────────────────────────────────────────────────────
// Evaluation types – mirrors the Python/FastAPI Pydantic models
// ──────────────────────────────────────────────────────────────

/** The high-level kind of AI model being evaluated. */
export type ModelType = "llm" | "stt" | "tts" | "vad" | "embeddings";

/** Where the model is expected to run. */
export type DeploymentTarget = "on-device" | "server" | "cloud-api";

/** Lifecycle status of an evaluation run. */
export type RunStatus =
  | "pending"
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

/** K-12 / higher-ed education tier. */
export type EducationTier = "elementary" | "highschool" | "undergrad" | "grad";

// ── Core entities ────────────────────────────────────────────

export interface EvalModel {
  id: string;
  name: string;
  slug: string;
  model_type: ModelType;
  source_type: string;
  deployment_target: DeploymentTarget;
  model_family?: string;
  model_version?: string;
  source_uri?: string;
  parameter_count_b?: number;
  model_size_gb?: number;
  quantization?: string;
  context_window?: number;
  education_tiers: string[];
  subjects: string[];
  tags: string[];
  is_reference: boolean;
  created_at: string;
}

export interface BenchmarkSuite {
  id: string;
  name: string;
  slug: string;
  model_type: string;
  description?: string;
  category?: string;
  is_builtin: boolean;
  task_count: number;
}

export interface EvalRun {
  id: string;
  model_id: string;
  suite_id: string;
  status: RunStatus;
  progress_percent: number;
  current_task?: string;
  tasks_completed: number;
  tasks_total: number;
  overall_score?: number;
  overall_metrics?: Record<string, any>;
  triggered_by: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  /** Joined / denormalized fields provided by the API for convenience. */
  model_name?: string;
  suite_name?: string;
}

export interface TaskResult {
  id: string;
  run_id: string;
  task_id: string;
  score?: number;
  raw_score?: number;
  raw_metric_name?: string;
  metrics: Record<string, any>;
  latency_ms?: number;
  status: string;
  task_name?: string;
  education_tier?: string;
  subject?: string;
}

export interface GradeLevelRating {
  model_id: string;
  run_id: string;
  tier_scores: Record<EducationTier, number>;
  max_passing_tier?: EducationTier;
  threshold: number;
  overall_education_score?: number;
  tier_details: Record<
    string,
    Array<{ task_name: string; score: number; weight: number }>
  >;
}

// ── Generic paginated envelope ───────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
