-- Initial schema for edu-voice-ai-eval

CREATE TABLE IF NOT EXISTS eval_models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    model_type TEXT NOT NULL,
    model_family TEXT,
    model_version TEXT,
    source_type TEXT NOT NULL,
    source_uri TEXT,
    source_format TEXT,
    api_base_url TEXT,
    api_key_env TEXT,
    deployment_target TEXT NOT NULL DEFAULT 'server',
    parameter_count_b REAL,
    model_size_gb REAL,
    quantization TEXT,
    context_window INTEGER,
    education_tiers TEXT,
    subjects TEXT,
    languages TEXT,
    tags TEXT,
    notes TEXT,
    is_reference BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_models_type ON eval_models(model_type);
CREATE INDEX IF NOT EXISTS idx_eval_models_family ON eval_models(model_family);
CREATE INDEX IF NOT EXISTS idx_eval_models_source ON eval_models(source_type);
CREATE INDEX IF NOT EXISTS idx_eval_models_deployment ON eval_models(deployment_target);

CREATE TABLE IF NOT EXISTS eval_benchmark_suites (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    model_type TEXT NOT NULL,
    config TEXT NOT NULL,
    default_params TEXT,
    category TEXT,
    is_builtin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_suites_type ON eval_benchmark_suites(model_type);

CREATE TABLE IF NOT EXISTS eval_benchmark_tasks (
    id TEXT PRIMARY KEY,
    suite_id TEXT NOT NULL REFERENCES eval_benchmark_suites(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL,
    config TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    education_tier TEXT,
    subject TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_tasks_suite ON eval_benchmark_tasks(suite_id);
CREATE INDEX IF NOT EXISTS idx_eval_tasks_tier ON eval_benchmark_tasks(education_tier);

CREATE TABLE IF NOT EXISTS eval_runs (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES eval_models(id),
    suite_id TEXT NOT NULL REFERENCES eval_benchmark_suites(id),
    run_config TEXT,
    run_params TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    progress_percent REAL DEFAULT 0,
    current_task TEXT,
    tasks_completed INTEGER DEFAULT 0,
    tasks_total INTEGER DEFAULT 0,
    queued_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    overall_score REAL,
    overall_metrics TEXT,
    hardware_info TEXT,
    software_info TEXT,
    error_message TEXT,
    error_traceback TEXT,
    schedule_id TEXT,
    triggered_by TEXT DEFAULT 'manual',
    run_version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_runs_model ON eval_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_eval_runs_suite ON eval_runs(suite_id);
CREATE INDEX IF NOT EXISTS idx_eval_runs_status ON eval_runs(status);
CREATE INDEX IF NOT EXISTS idx_eval_runs_created ON eval_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_eval_runs_model_suite ON eval_runs(model_id, suite_id);

CREATE TABLE IF NOT EXISTS eval_task_results (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    task_id TEXT NOT NULL REFERENCES eval_benchmark_tasks(id),
    score REAL,
    raw_score REAL,
    raw_metric_name TEXT,
    metrics TEXT,
    latency_ms REAL,
    throughput REAL,
    memory_peak_mb REAL,
    gpu_memory_peak_mb REAL,
    sample_audio_path TEXT,
    sample_text TEXT,
    status TEXT DEFAULT 'completed',
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    duration_seconds REAL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_task_results_run ON eval_task_results(run_id);
CREATE INDEX IF NOT EXISTS idx_eval_task_results_task ON eval_task_results(task_id);
CREATE INDEX IF NOT EXISTS idx_eval_task_results_score ON eval_task_results(score);

CREATE TABLE IF NOT EXISTS eval_baselines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    model_id TEXT NOT NULL REFERENCES eval_models(id),
    run_id TEXT NOT NULL REFERENCES eval_runs(id),
    suite_id TEXT NOT NULL REFERENCES eval_benchmark_suites(id),
    overall_score REAL NOT NULL,
    task_scores TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_baselines_model ON eval_baselines(model_id);
CREATE INDEX IF NOT EXISTS idx_eval_baselines_suite ON eval_baselines(suite_id);
CREATE INDEX IF NOT EXISTS idx_eval_baselines_active ON eval_baselines(is_active);

CREATE TABLE IF NOT EXISTS eval_custom_test_sets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    model_type TEXT NOT NULL,
    items TEXT NOT NULL,
    item_count INTEGER DEFAULT 0,
    tags TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS eval_queue (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'waiting',
    queued_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    required_gpu_memory_gb REAL,
    required_compute TEXT
);

CREATE INDEX IF NOT EXISTS idx_eval_queue_status ON eval_queue(status, priority DESC);

CREATE TABLE IF NOT EXISTS eval_schedules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    model_id TEXT REFERENCES eval_models(id),
    model_type TEXT,
    suite_id TEXT NOT NULL REFERENCES eval_benchmark_suites(id),
    schedule_type TEXT NOT NULL,
    cron_expression TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TEXT,
    next_run_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS eval_shared_reports (
    id TEXT PRIMARY KEY,
    share_token TEXT NOT NULL UNIQUE,
    report_type TEXT NOT NULL,
    report_config TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TEXT,
    view_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_eval_shared_token ON eval_shared_reports(share_token);
