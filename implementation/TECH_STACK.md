# Technology Stack

Every technology choice with rationale.

## Backend

### Python 3.11+
**Rationale:** lm-evaluation-harness is Python. UTMOS and WVMOS are Python. The transformers and datasets libraries are Python. The entire ML evaluation ecosystem speaks Python. No other language makes sense for the backend.

### FastAPI
**Rationale:** Modern async Python web framework with auto-generated OpenAPI docs, native WebSocket support, and Pydantic validation. Chosen over:
- **aiohttp** (used by UnaMentis management API): FastAPI's auto-docs and type-safe request validation are valuable for a standalone project where the API is a first-class interface
- **Flask**: No native async support
- **Django**: Too heavy for an API-only backend

### pluggy
**Rationale:** Battle-tested plugin framework (powers pytest). Enables clean separation between the core system and evaluation backends. Same framework used by the UnaMentis importers, so the pattern is proven.

### Click
**Rationale:** Standard Python CLI framework with subcommand support, auto-generated help text, and clean decorator syntax. Chosen over:
- **argparse**: Too verbose for complex CLIs
- **Typer**: Nice, but Click is more mature and has better subcommand grouping

### SQLite (default) / PostgreSQL (team)
**Rationale:** SQLite is zero-config, single-file, and perfect for individual use. PostgreSQL adds concurrent access for team deployments. The schema is designed to work with both. Chosen over:
- **MongoDB**: Relational queries (joins, aggregations) are core to comparison and trend analysis
- **File-based JSON**: Too slow for filtering and aggregation once you have hundreds of runs

### Celery + Redis (optional)
**Rationale:** GPU evaluations can take hours. Celery provides robust background task execution with retry logic, priority queues, and distributed workers. Optional because development mode uses asyncio directly. Redis as broker is lightweight and widely deployed.

### hatchling
**Rationale:** Modern Python build system supporting PEP 621 (`pyproject.toml`). Enables entry point registration for CLI (`voicelearn-eval`) and plugins. Chosen over:
- **setuptools**: Works but more configuration
- **poetry**: Good but hatchling is more standards-aligned

## Frontend

### Next.js 16 + React 19
**Rationale:** The UnaMentis web console already uses this stack. Enables component reuse and pattern familiarity. App Router provides server-side rendering for the dashboard pages. React 19's concurrent features help with large data visualizations.

### Tailwind CSS 4
**Rationale:** Utility-first CSS, already used across UnaMentis. Fast styling with dark theme support built-in. No separate CSS files to manage.

### ECharts
**Rationale:** Comprehensive charting library that handles all needed chart types: heatmaps (grade-level matrix), scatter plots (quality vs. performance), line charts (trends), bar charts (WER breakdown), radar charts (model comparison). Already used in the UnaMentis latency dashboard.

Chosen over:
- **D3.js**: More flexible but much more code per chart
- **Chart.js**: Doesn't handle heatmaps and radar charts as well
- **Recharts**: Good for simple charts, but ECharts handles complex visualizations better

### TypeScript (strict mode)
**Rationale:** Type safety catches bugs at compile time, improves IDE experience, and serves as documentation. All component props and API responses are typed.

## Evaluation Tools (Upstream)

### lm-evaluation-harness (EleutherAI)
**Version:** >=0.4
**Role:** Core LLM benchmarking
**Integration:** Python API (primary) + subprocess (isolation fallback)
**License:** MIT

### transformers + datasets (HuggingFace)
**Role:** Model loading and dataset access for STT/TTS evaluation
**Integration:** Direct Python library usage

### jiwer
**Version:** >=3.0
**Role:** WER/CER computation for STT evaluation
**Integration:** Direct Python library usage

### UTMOS (torch + torchaudio)
**Role:** Automated MOS scoring for TTS
**Integration:** torch.hub model loading

### WVMOS
**Role:** Complementary MOS scoring
**Integration:** Direct Python library usage

### Montreal Forced Aligner (optional)
**Role:** Phoneme alignment for pronunciation evaluation
**Integration:** CLI wrapper

## Infrastructure

### Docker
**Rationale:** Reproducible evaluation environments. GPU passthrough for CUDA evaluations. Single `docker compose up` deployment.

### GitHub Actions
**Rationale:** CI/CD for automated evaluation triggered by schedules or new model releases. Self-hosted runners for GPU access.

## Data Formats

### VLEF (Voice Learning Eval Format)
**Format:** JSON
**Purpose:** Portable results sharing
**Rationale:** JSON is universally readable. No binary format needed since evaluation results are metadata (scores and metrics), not large binary data.

### YAML (configurations)
**Rationale:** lm-evaluation-harness already uses YAML for task definitions. Human-readable and widely supported.

### TOML (project configuration)
**Rationale:** `pyproject.toml` is the Python standard. Also used for application-level config alongside YAML.

## What We Deliberately Avoid

| Technology | Why Not |
|-----------|---------|
| **Kubernetes** | Overkill for an evaluation tool. Docker Compose is sufficient. |
| **GraphQL** | REST is simpler and the API surface is straightforward CRUD + queries. |
| **NoSQL databases** | Relational queries are core to comparison and trend analysis. |
| **Custom ML frameworks** | We wrap existing tools, not build new ones. |
| **Electron/desktop app** | Web dashboard + CLI covers all use cases. |
| **Microservices** | Single Python process + separate web frontend is the right granularity. |

## Version Compatibility

| Component | Minimum Version | Tested With |
|-----------|----------------|------------|
| Python | 3.11 | 3.11, 3.12 |
| Node.js | 20 LTS | 20, 22 |
| CUDA | 11.8 | 11.8, 12.x |
| SQLite | 3.35 (JSON support) | System default |
| PostgreSQL | 14 | 14, 15, 16 |
