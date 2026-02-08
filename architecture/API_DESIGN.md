# REST API Design

FastAPI backend serving the web dashboard and supporting external integrations. Auto-generates OpenAPI documentation at `/docs`.

**Base URL:** `http://localhost:8790`

## Endpoints

### Models

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/models` | List registered models |
| POST | `/api/eval/models` | Register a new model |
| GET | `/api/eval/models/{id}` | Get model details |
| PATCH | `/api/eval/models/{id}` | Update model metadata |
| DELETE | `/api/eval/models/{id}` | Remove model (soft delete) |
| POST | `/api/eval/models/import-hf` | Import model from HuggingFace |
| GET | `/api/eval/models/{id}/runs` | List all runs for a model |
| GET | `/api/eval/models/{id}/grade` | Get latest grade-level rating |

**Query parameters for `GET /api/eval/models`:**
```
?model_type=llm                    # Filter by type
&deployment_target=on-device       # Filter by target
&model_family=qwen                 # Filter by family
&is_reference=true                 # Only reference models
&search=qwen                       # Full-text search
&limit=20&offset=0                 # Pagination
```

**POST `/api/eval/models` body:**
```json
{
  "name": "Qwen 2.5 3B Instruct",
  "model_type": "llm",
  "source_type": "huggingface",
  "source_uri": "Qwen/Qwen2.5-3B-Instruct",
  "deployment_target": "server",
  "parameter_count_b": 3.0,
  "quantization": "FP16",
  "context_window": 32768,
  "languages": ["en", "zh"],
  "tags": ["instruction-tuned", "multilingual"]
}
```

**POST `/api/eval/models/import-hf` body:**
```json
{
  "repo_id": "Qwen/Qwen2.5-3B-Instruct",
  "model_type": "llm",
  "deployment_target": "server"
}
```
Auto-populates parameters, size, and other metadata from HuggingFace Hub.

### Benchmark Suites

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/suites` | List benchmark suites |
| POST | `/api/eval/suites` | Create custom suite |
| GET | `/api/eval/suites/{id}` | Get suite with tasks |
| PATCH | `/api/eval/suites/{id}` | Update suite |
| DELETE | `/api/eval/suites/{id}` | Remove custom suite |
| GET | `/api/eval/benchmarks` | List all benchmarks (all plugins) |

**Query parameters for `GET /api/eval/suites`:**
```
?model_type=llm                    # Filter by model type
&category=education                # Filter by category
&is_builtin=true                   # Only built-in suites
```

### Evaluation Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/eval/runs` | Start a new evaluation run |
| GET | `/api/eval/runs` | List runs with filters |
| GET | `/api/eval/runs/{id}` | Get run details |
| POST | `/api/eval/runs/{id}/cancel` | Cancel a running evaluation |
| GET | `/api/eval/runs/{id}/results` | Get detailed task results |
| GET | `/api/eval/runs/{id}/progress` | Get current progress |
| DELETE | `/api/eval/runs/{id}` | Delete a run and its results |

**POST `/api/eval/runs` body:**
```json
{
  "model_id": "model_abc123",
  "suite_id": "education_focus",
  "config": {
    "gpu": "cuda:0",
    "batch_size": 8,
    "timeout": 3600
  },
  "priority": 5
}
```

**Response (201 Created):**
```json
{
  "id": "run_xyz789",
  "model_id": "model_abc123",
  "suite_id": "education_focus",
  "status": "queued",
  "tasks_total": 12,
  "created_at": "2026-02-08T10:30:00Z"
}
```

**Query parameters for `GET /api/eval/runs`:**
```
?status=completed                  # Filter by status
&model_id=model_abc123             # Filter by model
&suite_id=education_focus          # Filter by suite
&triggered_by=manual               # Filter by trigger type
&sort=-created_at                  # Sort (prefix - for desc)
&limit=20&offset=0                 # Pagination
```

**GET `/api/eval/runs/{id}/results` response:**
```json
{
  "run_id": "run_xyz789",
  "model": { "id": "...", "name": "Qwen 2.5 3B" },
  "suite": { "id": "...", "name": "Education Focus" },
  "overall_score": 72.3,
  "status": "completed",
  "results": [
    {
      "task_id": "task_001",
      "task_name": "Tier 1: GSM8K",
      "benchmark_id": "edu_tier1_gsm8k",
      "score": 82.3,
      "raw_score": 0.823,
      "raw_metric_name": "accuracy",
      "metrics": {
        "accuracy": 0.823,
        "exact_match": 0.801
      },
      "education_tier": "elementary",
      "duration_seconds": 145.2
    }
  ],
  "grade_level": {
    "tier_scores": {
      "elementary": 85.2,
      "highschool": 72.1,
      "undergrad": 48.3,
      "grad": 22.7
    },
    "max_passing_tier": "highschool",
    "threshold": 70
  }
}
```

### Queue

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/queue` | Get current evaluation queue |
| PATCH | `/api/eval/queue/{id}/priority` | Change queue priority |

### Comparison

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/compare` | Compare models |
| POST | `/api/eval/compare/save` | Save a comparison for sharing |

**Query parameters for `GET /api/eval/compare`:**
```
?model_ids=id1,id2,id3            # Models to compare (2-5)
&benchmark_ids=bench1,bench2       # Optional: specific benchmarks
&suite_id=education_focus          # Optional: compare within suite
```

**Response:**
```json
{
  "models": [
    { "id": "...", "name": "Qwen 2.5 3B" },
    { "id": "...", "name": "Ministral 3B" }
  ],
  "tasks": [
    {
      "task_name": "Tier 1: GSM8K",
      "scores": { "model_id_1": 82.3, "model_id_2": 78.1 },
      "best_model_id": "model_id_1"
    }
  ],
  "radar_dimensions": [
    { "name": "Math", "values": { "model_id_1": 82, "model_id_2": 78 } },
    { "name": "Science", "values": { "model_id_1": 75, "model_id_2": 71 } }
  ],
  "summary": {
    "overall_scores": { "model_id_1": 72.3, "model_id_2": 68.1 },
    "recommendation": "Qwen 2.5 3B scores higher across education tiers."
  }
}
```

### Grade-Level Matrix

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/grade-matrix` | Grade-level capability matrix |
| GET | `/api/eval/grade-matrix/{model_id}` | Grade-level for one model |

**Query parameters for `GET /api/eval/grade-matrix`:**
```
?deployment_target=on-device       # Filter by deployment target
&model_type=llm                    # Filter by type
&threshold=0.70                    # Passing threshold
```

**Response:**
```json
{
  "threshold": 0.70,
  "rows": [
    {
      "model": { "id": "...", "name": "Qwen 2.5 3B", "parameter_count_b": 3.0 },
      "tiers": {
        "elementary": { "score": 85.2, "pass": true, "task_count": 3 },
        "highschool": { "score": 72.1, "pass": true, "task_count": 5 },
        "undergrad": { "score": 48.3, "pass": false, "task_count": 3 },
        "grad": { "score": 22.7, "pass": false, "task_count": 2 }
      },
      "max_passing_tier": "highschool",
      "overall_score": 57.1
    }
  ]
}
```

### Trends

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/trends` | Historical trend data |

**Query parameters:**
```
?model_family=qwen                 # Track a model family over versions
&benchmark_id=edu_tier2_arc        # Specific benchmark
&since=2025-01-01                  # Time range
```

### Baselines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/baselines` | List baselines |
| POST | `/api/eval/baselines` | Create baseline from a run |
| GET | `/api/eval/baselines/{id}/check` | Check run against baseline |
| DELETE | `/api/eval/baselines/{id}` | Remove baseline |

### Reports & Sharing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/eval/reports/export` | Export results (JSON, CSV, VLEF) |
| POST | `/api/eval/reports/import` | Import VLEF file |
| POST | `/api/eval/share` | Create share link |
| GET | `/api/eval/share/{token}` | Get shared report data |

### Custom Test Sets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/eval/test-sets` | List custom test sets |
| POST | `/api/eval/test-sets` | Create custom test set |
| GET | `/api/eval/test-sets/{id}` | Get test set details |
| DELETE | `/api/eval/test-sets/{id}` | Remove test set |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| WS `/api/eval/ws` | Real-time progress updates |

**WebSocket message format:**
```json
{
  "type": "progress",
  "run_id": "run_xyz789",
  "task_name": "Tier 2: ARC Challenge",
  "task_index": 5,
  "total_tasks": 12,
  "percent_complete": 41.7,
  "message": "Running ARC Challenge evaluation..."
}
```

```json
{
  "type": "completed",
  "run_id": "run_xyz789",
  "overall_score": 72.3,
  "grade_level": "highschool"
}
```

## Error Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model with ID 'xyz' not found",
    "details": {}
  }
}
```

| HTTP Status | Error Codes |
|-------------|-------------|
| 400 | INVALID_REQUEST, INVALID_CONFIG |
| 404 | MODEL_NOT_FOUND, RUN_NOT_FOUND, SUITE_NOT_FOUND |
| 409 | RUN_ALREADY_RUNNING, DUPLICATE_MODEL |
| 422 | VALIDATION_ERROR |
| 500 | INTERNAL_ERROR, PLUGIN_ERROR |
| 503 | GPU_UNAVAILABLE, QUEUE_FULL |

## Authentication

No authentication by default (local tool). For team deployments, optional API key authentication:

```
Authorization: Bearer <api-key>
```

Configured via environment variable `VOICELEARN_EVAL_API_KEY`. When set, all endpoints require the header.
