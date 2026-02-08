# Implementation Roadmap

Five phases from foundation to community release.

## Phase 1: Foundation (Weeks 1-3)

**Goal:** Core infrastructure working end-to-end. A user can evaluate an LLM on education benchmarks via CLI and see grade-level results.

### Tasks

1. **Project scaffolding**
   - `pyproject.toml` with hatchling build system
   - Package structure: `voicelearn_eval/` with core, plugins, storage, cli modules
   - Development dependencies: pytest, ruff, mypy
   - Basic CI: lint + test on push

2. **Data models** (`voicelearn_eval/core/models.py`)
   - All dataclasses from [DATA_MODEL.md](../architecture/DATA_MODEL.md)
   - `to_dict()` / `from_dict()` serialization
   - Pydantic models for API validation

3. **SQLite storage** (`voicelearn_eval/storage/`)
   - Schema creation and migration
   - CRUD operations for all entities
   - Query methods with filtering and pagination

4. **Plugin system** (`voicelearn_eval/plugins/`)
   - Hook specifications and base plugin class
   - Plugin registry with entry point discovery
   - Score normalization utilities

5. **LLM evaluation plugin** (`voicelearn_eval/plugins/llm/lm_eval_harness.py`)
   - Wrap lm-evaluation-harness (Python API + subprocess fallback)
   - Map MMLU subjects to education tiers
   - Support HuggingFace, GGUF, and API models

6. **Grade-level system** (`voicelearn_eval/grade_levels/`)
   - Tier definitions and benchmark-to-tier mapping
   - Threshold-based pass/fail scoring
   - Maximum passing tier calculation

7. **CLI** (`voicelearn_eval/cli/`)
   - `run` command: evaluate a model on a suite
   - `list` command: models, benchmarks, runs, suites
   - `grade` command: grade-level assessment
   - Table output formatting

8. **VLEF export/import**
   - JSON-based portable format v1.0
   - `export` and `import` CLI commands

### Deliverable

```bash
pip install -e .
voicelearn-eval run --model Qwen/Qwen2.5-3B-Instruct --suite education_focus --gpu cuda:0
voicelearn-eval grade --model Qwen/Qwen2.5-3B-Instruct
# Output: Grade-level table showing Tier 1: PASS, Tier 2: PASS, Tier 3: FAIL, Tier 4: FAIL
```

---

## Phase 2: Dashboard + STT/TTS (Weeks 4-6)

**Goal:** Web dashboard operational with grade-level matrix visualization. STT and TTS evaluation working.

### Tasks

1. **FastAPI backend** (`voicelearn_eval/api/`)
   - Application setup with CORS, error handling
   - All REST endpoints from [API_DESIGN.md](../architecture/API_DESIGN.md)
   - WebSocket endpoint for live progress
   - OpenAPI documentation auto-generated

2. **Orchestrator** (`voicelearn_eval/core/orchestrator.py`)
   - Evaluation run lifecycle management
   - Progress tracking and WebSocket broadcasting
   - Asyncio-based job execution (no Celery yet)

3. **Next.js web dashboard** (`web/`)
   - Project scaffolding: Next.js 16 + React 19 + Tailwind CSS 4
   - Dark theme, layout with navigation
   - ECharts wrapper component

4. **Dashboard pages (initial)**
   - Overview Dashboard (stats, recent runs)
   - Grade-Level Matrix (the signature view, ECharts heatmap)
   - Model Registry (list, detail, HuggingFace import)
   - Evaluation Runs (list, detail with progress)

5. **STT evaluation plugin** (`voicelearn_eval/plugins/stt/`)
   - WER computation using jiwer
   - Standard dataset evaluation (LibriSpeech, CommonVoice)
   - Custom educational vocabulary evaluation
   - RTFx and latency measurement

6. **TTS evaluation plugin** (`voicelearn_eval/plugins/tts/`)
   - UTMOS integration for automated MOS
   - WVMOS integration
   - Intelligibility round-trip (TTS -> STT -> WER)
   - Audio sample storage

7. **`serve` CLI command**
   - Starts FastAPI + Next.js dev server
   - Auto-opens browser

### Deliverable

```bash
voicelearn-eval serve
# Opens http://localhost:3001 with grade-level matrix, model cards, run history
```

---

## Phase 3: Comparison + CI/CD (Weeks 7-9)

**Goal:** Full comparison workflow, historical trends, CI integration, shareable results.

### Tasks

1. **Model Comparison page**
   - Comparison builder (select 2-5 models)
   - Side-by-side results table with delta highlighting
   - Radar chart (multi-dimensional capability)
   - API: `GET /api/eval/compare`

2. **Results Dashboard (full)**
   - Quality vs Performance scatter plot
   - Delta from Reference bar chart
   - Benchmark breakdown table
   - STT-specific detail view (WER by dataset, domain heatmap)
   - TTS-specific detail view (MOS, pronunciation, audio player)

3. **Historical Trends**
   - Track model family performance over versions
   - Line charts with release date markers
   - API: `GET /api/eval/trends`

4. **Regression detection**
   - Baseline creation and management
   - Compare new run against baseline
   - Severity levels (minor, moderate, severe)
   - Alert in dashboard when regression detected

5. **GitHub Actions workflows**
   - `evaluate.yml`: Run evaluation on demand or schedule
   - `new_model.yml`: Periodic check for new HuggingFace models
   - CI mode: `--ci` flag with structured exit codes

6. **VLEF sharing**
   - Export/import via CLI and web UI
   - Shared report links with tokens
   - Reports page in dashboard

7. **Pronunciation evaluation**
   - Montreal Forced Aligner integration
   - Phoneme comparison and PER calculation
   - Pronunciation challenge test set

### Deliverable

Full comparison workflow: evaluate multiple models, compare side-by-side, track improvements over time, share results with colleagues.

---

## Phase 4: Education Benchmarks + Polish (Weeks 10-12)

**Goal:** Education-specific benchmarks integrated, Docker packaging, documentation, ready for standalone release.

### Tasks

1. **TutorBench integration**
   - Load dataset from HuggingFace
   - LLM-judge scoring using rubrics
   - Map scores to grade-level system

2. **OpenLearnLM integration**
   - Subset of 5,000 items across Bloom's taxonomy levels
   - Custom lm-eval-harness task definitions
   - Bloom's level breakdown in results

3. **Custom domain test sets**
   - Educational vocabulary audio generation pipeline
   - Test set editor in web UI
   - Per-subject WER analysis for STT

4. **On-device performance metrics**
   - System monitor during evaluation (CPU, memory, GPU)
   - Token throughput measurement
   - Model load time tracking
   - On-device feasibility scoring

5. **Benchmark Suites management page**
   - Browse built-in suites
   - Create custom suites from web UI
   - Configure suite parameters

6. **Docker packaging**
   - `Dockerfile` for the Python backend + evaluation tools
   - `docker-compose.yml` for full stack (API + web + optional Redis)
   - GPU passthrough configuration
   - Volume mounts for results persistence

7. **Documentation**
   - README with quick start, installation, usage
   - Contributing guide
   - API documentation (auto-generated from FastAPI)
   - Architecture documentation (this folder, updated)

8. **Standalone extraction**
   - Remove any UnaMentis-specific references
   - Verify all dependencies are declared in pyproject.toml
   - Test clean installation from PyPI or GitHub
   - Publish to GitHub as `edu-voice-ai-eval`

### Deliverable

```bash
# Docker deployment
docker compose up
# Visit http://localhost:3001

# Or pip install
pip install edu-voice-ai-eval
voicelearn-eval serve
```

---

## Phase 5: Community + Scale (Ongoing)

**Goal:** Community features, broader model coverage, and production hardening.

### Tasks

1. **HuggingFace auto-detection**
   - Webhook or polling for new model releases
   - Auto-register models matching tracked families
   - Auto-trigger evaluation on new models

2. **Community test sets**
   - Upload and share custom domain test sets
   - Test set marketplace or registry
   - Contribution guidelines

3. **Leaderboard**
   - Optional hosted leaderboard for public results
   - Configurable privacy (private, unlisted, public)

4. **VAD + Embeddings plugins**
   - Complete all five model categories
   - VAD: detection accuracy, false positive rate
   - Embeddings: MTEB benchmark integration

5. **Multilingual expansion**
   - Non-English benchmark datasets
   - Multilingual educational vocabulary test sets
   - Language-specific grade-level mapping

6. **Celery worker mode**
   - Distributed evaluation across multiple GPU workers
   - Redis-based job queue
   - Worker health monitoring

7. **Production hardening**
   - PostgreSQL migration scripts
   - API authentication
   - Rate limiting
   - Monitoring and alerting (Prometheus metrics)

---

## Milestone Summary

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| 1 | Weeks 1-3 | CLI evaluates LLMs with grade-level ratings |
| 2 | Weeks 4-6 | Web dashboard with grade-level matrix |
| 3 | Weeks 7-9 | Full comparison, trends, CI/CD, sharing |
| 4 | Weeks 10-12 | Education benchmarks, Docker, standalone release |
| 5 | Ongoing | Community features, scale, multilingual |
