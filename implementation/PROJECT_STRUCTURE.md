# Project Structure

Complete folder layout for the `edu-voice-ai-eval` repository.

```
edu-voice-ai-eval/
│
├── README.md                                  # Project overview, quick start
├── ATTRIBUTION.md                             # Credits to upstream projects
├── LICENSE                                    # MIT
├── CHANGELOG.md                               # Release notes
├── pyproject.toml                             # Python packaging (PEP 621, hatchling)
├── Dockerfile                                 # Python backend + eval tools
├── docker-compose.yml                         # Full stack deployment
├── .github/
│   └── workflows/
│       ├── ci.yml                             # Lint + test on push
│       ├── evaluate.yml                       # On-demand or scheduled evaluation
│       └── new_model.yml                      # Periodic new model detection
│
├── voicelearn_eval/                           # Core Python package
│   ├── __init__.py                            # Package version
│   ├── __main__.py                            # Entry: python -m voicelearn_eval
│   │
│   ├── core/                                  # Core domain logic
│   │   ├── __init__.py
│   │   ├── models.py                          # Dataclasses: ModelSpec, EvalRun, EvalResult, etc.
│   │   ├── orchestrator.py                    # Evaluation pipeline orchestrator
│   │   ├── scheduler.py                       # Cron-based and webhook scheduling
│   │   └── config.py                          # YAML/TOML configuration loading
│   │
│   ├── plugins/                               # Evaluation backend plugins
│   │   ├── __init__.py
│   │   ├── base.py                            # Hook specs, BaseEvalPlugin, PluginRegistry
│   │   ├── runner.py                          # Subprocess plugin runner (isolation)
│   │   │
│   │   ├── llm/                               # LLM evaluation
│   │   │   ├── __init__.py
│   │   │   ├── lm_eval_harness.py             # EleutherAI wrapper
│   │   │   └── deepeval_plugin.py             # DeepEval wrapper (optional)
│   │   │
│   │   ├── stt/                               # STT evaluation
│   │   │   ├── __init__.py
│   │   │   ├── open_asr.py                    # Open ASR Leaderboard methodology
│   │   │   ├── picovoice_metrics.py           # Picovoice performance metrics
│   │   │   └── domain_wer.py                  # Custom educational domain WER
│   │   │
│   │   ├── tts/                               # TTS evaluation
│   │   │   ├── __init__.py
│   │   │   ├── quality.py                     # UTMOS + WVMOS MOS scoring
│   │   │   ├── intelligibility.py             # STT round-trip WER
│   │   │   ├── pronunciation.py               # Forced alignment pronunciation eval
│   │   │   └── prosody.py                     # Pitch/rate/pause analysis
│   │   │
│   │   ├── vad/                               # VAD evaluation (Phase 5)
│   │   │   ├── __init__.py
│   │   │   └── vad_eval.py
│   │   │
│   │   └── embeddings/                        # Embedding evaluation (Phase 5)
│   │       ├── __init__.py
│   │       └── mteb_plugin.py                 # MTEB benchmark wrapper
│   │
│   ├── grade_levels/                          # Education grade-level system
│   │   ├── __init__.py
│   │   ├── tiers.py                           # Tier definitions and constants
│   │   ├── mmlu_mapping.py                    # MMLU subject -> tier mapping
│   │   └── scorer.py                          # Score calculation, pass/fail, max tier
│   │
│   ├── storage/                               # Persistence layer
│   │   ├── __init__.py
│   │   ├── base.py                            # Abstract storage interface
│   │   ├── sqlite_storage.py                  # SQLite implementation
│   │   ├── postgresql_storage.py              # PostgreSQL implementation
│   │   └── migrations/                        # Schema migrations
│   │       ├── __init__.py
│   │       └── 001_initial.sql
│   │
│   ├── analyzer/                              # Results analysis
│   │   ├── __init__.py
│   │   ├── statistics.py                      # Aggregate scores, confidence intervals
│   │   ├── comparisons.py                     # Multi-model comparison logic
│   │   ├── trends.py                          # Historical trend analysis
│   │   ├── regression.py                      # Regression detection against baselines
│   │   └── recommendations.py                 # Automated deployment recommendations
│   │
│   ├── integrations/                          # External service integrations
│   │   ├── __init__.py
│   │   ├── huggingface.py                     # HF Hub model search and metadata
│   │   ├── ollama.py                          # Ollama model discovery
│   │   └── openai_compat.py                   # OpenAI-compatible API registration
│   │
│   ├── api/                                   # FastAPI REST API
│   │   ├── __init__.py
│   │   ├── app.py                             # FastAPI application factory
│   │   ├── dependencies.py                    # Dependency injection
│   │   ├── websocket.py                       # WebSocket for live progress
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── models.py                      # /api/eval/models
│   │       ├── suites.py                      # /api/eval/suites
│   │       ├── runs.py                        # /api/eval/runs
│   │       ├── results.py                     # /api/eval/results
│   │       ├── compare.py                     # /api/eval/compare
│   │       ├── grade_matrix.py                # /api/eval/grade-matrix
│   │       ├── trends.py                      # /api/eval/trends
│   │       ├── baselines.py                   # /api/eval/baselines
│   │       ├── reports.py                     # /api/eval/reports
│   │       ├── test_sets.py                   # /api/eval/test-sets
│   │       └── share.py                       # /api/eval/share
│   │
│   ├── cli/                                   # Click CLI
│   │   ├── __init__.py
│   │   ├── main.py                            # Top-level CLI group
│   │   ├── run.py                             # voicelearn-eval run
│   │   ├── list_cmd.py                        # voicelearn-eval list
│   │   ├── compare.py                         # voicelearn-eval compare
│   │   ├── grade.py                           # voicelearn-eval grade
│   │   ├── model.py                           # voicelearn-eval model
│   │   ├── suite.py                           # voicelearn-eval suite
│   │   ├── export_import.py                   # voicelearn-eval export/import
│   │   ├── serve.py                           # voicelearn-eval serve
│   │   ├── plugin.py                          # voicelearn-eval plugin
│   │   └── schedule.py                        # voicelearn-eval schedule
│   │
│   └── vlef/                                  # VLEF format handling
│       ├── __init__.py
│       ├── exporter.py                        # Export to VLEF JSON
│       └── importer.py                        # Import from VLEF JSON
│
├── web/                                       # Next.js web dashboard
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── app/
│       │   ├── layout.tsx                     # Root layout with navigation
│       │   ├── page.tsx                       # Overview dashboard
│       │   ├── models/
│       │   │   └── page.tsx                   # Model registry
│       │   ├── runs/
│       │   │   ├── page.tsx                   # Evaluation runs list
│       │   │   └── [id]/
│       │   │       └── page.tsx               # Run detail
│       │   ├── results/
│       │   │   └── page.tsx                   # Results dashboard
│       │   ├── compare/
│       │   │   └── page.tsx                   # Model comparison
│       │   ├── benchmarks/
│       │   │   └── page.tsx                   # Benchmark suite management
│       │   ├── reports/
│       │   │   └── page.tsx                   # Reports and sharing
│       │   ├── share/
│       │   │   └── [token]/
│       │   │       └── page.tsx               # Public shared report
│       │   └── api/                           # API proxy routes
│       │       └── eval/
│       │           └── [...path]/
│       │               └── route.ts           # Proxy to FastAPI backend
│       │
│       ├── components/
│       │   ├── charts/                        # ECharts wrappers
│       │   │   ├── EChartsWrapper.tsx
│       │   │   ├── GradeLevelMatrix.tsx       # Heatmap for grade-level view
│       │   │   ├── QualityPerformanceScatter.tsx
│       │   │   ├── FamilyTrendChart.tsx
│       │   │   ├── DeltaFromReference.tsx
│       │   │   ├── RadarChart.tsx
│       │   │   ├── WERBarChart.tsx
│       │   │   ├── DomainWERHeatmap.tsx
│       │   │   └── MOSComparisonChart.tsx
│       │   │
│       │   ├── dashboard/
│       │   │   ├── OverviewPanel.tsx
│       │   │   ├── RecentRunsTable.tsx
│       │   │   └── NavBar.tsx
│       │   │
│       │   ├── models/
│       │   │   ├── ModelRegistryPanel.tsx
│       │   │   ├── ModelCard.tsx
│       │   │   ├── ModelFilterBar.tsx
│       │   │   └── HuggingFaceImportModal.tsx
│       │   │
│       │   ├── runs/
│       │   │   ├── RunsPanel.tsx
│       │   │   ├── ActiveRunCard.tsx
│       │   │   ├── QueueList.tsx
│       │   │   └── CompletedRunsTable.tsx
│       │   │
│       │   ├── results/
│       │   │   ├── ResultsPanel.tsx
│       │   │   ├── STTDetailPanel.tsx
│       │   │   ├── TTSDetailPanel.tsx
│       │   │   ├── AudioSamplePlayer.tsx
│       │   │   └── BenchmarkBreakdownTable.tsx
│       │   │
│       │   ├── compare/
│       │   │   ├── ComparisonPanel.tsx
│       │   │   ├── ComparisonBuilder.tsx
│       │   │   └── ComparisonTable.tsx
│       │   │
│       │   └── ui/                            # Shared UI components
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── stat-card.tsx
│       │       ├── badge.tsx
│       │       ├── tabs.tsx
│       │       ├── table.tsx
│       │       ├── modal.tsx
│       │       ├── progress-bar.tsx
│       │       └── tooltip.tsx
│       │
│       ├── hooks/
│       │   ├── useEvalData.ts                 # Data fetching with auto-refresh
│       │   ├── useEvalModels.ts
│       │   ├── useEvalRuns.ts
│       │   ├── useComparison.ts
│       │   └── useWebSocket.ts                # WebSocket for live progress
│       │
│       ├── lib/
│       │   ├── api-client.ts                  # Fetch wrapper for eval API
│       │   ├── chart-transforms.ts            # Data -> ECharts option transforms
│       │   └── utils.ts                       # cn(), formatters
│       │
│       └── types/
│           └── evaluation.ts                  # All TypeScript types
│
├── test_sets/                                 # Educational evaluation data
│   ├── stt/
│   │   ├── educational_vocabulary/
│   │   │   ├── tier1_elementary.json
│   │   │   ├── tier2_high_school.json
│   │   │   ├── tier3_undergraduate.json
│   │   │   └── tier4_graduate.json
│   │   └── audio/                             # Generated audio files
│   │       └── .gitkeep
│   ├── tts/
│   │   ├── pronunciation_challenges/
│   │   │   ├── science_terms.json
│   │   │   ├── math_terms.json
│   │   │   ├── history_terms.json
│   │   │   └── technical_terms.json
│   │   ├── test_sentences/
│   │   │   ├── standard_100.json
│   │   │   └── educational_50.json
│   │   └── listenability/
│   │       └── long_form_passages.json
│   └── llm/
│       ├── custom_tasks/                      # lm-eval-harness YAML tasks
│       │   ├── edu_tier1.yaml
│       │   ├── edu_tier2.yaml
│       │   ├── edu_tier3.yaml
│       │   ├── edu_tier4.yaml
│       │   ├── tutorbench_adaptive.yaml
│       │   └── openlearnlm_subset.yaml
│       └── conversation_scenarios/
│           └── tutoring_dialogues.json
│
├── configs/                                   # Evaluation configuration files
│   ├── default.yaml                           # Default config
│   ├── quick_scan.yaml                        # Fast model check (~5 min)
│   ├── education_focus.yaml                   # Full education eval (~30 min)
│   ├── full_llm.yaml                          # Comprehensive LLM (~2 hrs)
│   ├── stt_standard.yaml                      # Standard STT benchmarks
│   ├── stt_education.yaml                     # STT + educational domain
│   ├── tts_quality.yaml                       # Full TTS quality assessment
│   └── on_device.yaml                         # On-device focused evaluation
│
├── docs/                                      # Architecture documentation
│   ├── architecture/                          # (Promoted from this folder)
│   ├── benchmarks/
│   └── implementation/
│
└── tests/                                     # Python test suite
    ├── conftest.py                            # Shared fixtures
    ├── test_core/
    │   ├── test_models.py
    │   ├── test_orchestrator.py
    │   └── test_config.py
    ├── test_plugins/
    │   ├── test_base.py
    │   ├── test_registry.py
    │   ├── test_lm_eval_harness.py
    │   ├── test_stt_eval.py
    │   └── test_tts_eval.py
    ├── test_grade_levels/
    │   ├── test_tiers.py
    │   ├── test_mmlu_mapping.py
    │   └── test_scorer.py
    ├── test_storage/
    │   ├── test_sqlite.py
    │   └── test_migrations.py
    ├── test_analyzer/
    │   ├── test_statistics.py
    │   ├── test_comparisons.py
    │   └── test_regression.py
    ├── test_api/
    │   ├── test_models_api.py
    │   ├── test_runs_api.py
    │   └── test_compare_api.py
    ├── test_cli/
    │   ├── test_run_cmd.py
    │   ├── test_grade_cmd.py
    │   └── test_serve_cmd.py
    └── test_vlef/
        ├── test_export.py
        └── test_import.py
```

## File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `voicelearn_eval/` | ~50 | Core Python package |
| `web/src/` | ~45 | Next.js dashboard |
| `test_sets/` | ~15 | Educational evaluation data |
| `configs/` | ~8 | Predefined configurations |
| `tests/` | ~20 | Python test suite |
| **.github/** | ~3 | CI/CD workflows |
| **Root** | ~6 | Project files |
| **Total** | ~150 | |

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "edu-voice-ai-eval"
version = "0.1.0"
description = "Unified AI model evaluation for educational voice interaction"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [{ name = "UnaMentis" }]

dependencies = [
    "click>=8.0",
    "fastapi>=0.100",
    "uvicorn>=0.20",
    "websockets>=12.0",
    "pluggy>=1.0",
    "pydantic>=2.0",
    "aiosqlite>=0.19",
    "jiwer>=3.0",
    "huggingface-hub>=0.20",
    "pyyaml>=6.0",
    "rich>=13.0",          # CLI table formatting
    "tabulate>=0.9",       # Table output
]

[project.optional-dependencies]
llm = [
    "lm-eval>=0.4",
    "transformers>=4.40",
    "torch>=2.0",
    "accelerate>=0.25",
]
stt = [
    "transformers>=4.40",
    "datasets>=2.18",
    "torch>=2.0",
    "torchaudio>=2.0",
    "soundfile>=0.12",
]
tts = [
    "torch>=2.0",
    "torchaudio>=2.0",
    "wvmos>=0.3",
]
all = ["edu-voice-ai-eval[llm,stt,tts]"]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.3",
    "mypy>=1.8",
    "httpx>=0.27",         # API testing
]
postgresql = ["asyncpg>=0.29"]
celery = ["celery>=5.3", "redis>=5.0"]

[project.scripts]
voicelearn-eval = "voicelearn_eval.cli.main:cli"

[project.entry-points."voicelearn_eval.plugins"]
lm_eval_harness = "voicelearn_eval.plugins.llm.lm_eval_harness:LMEvalHarnessPlugin"
stt_eval = "voicelearn_eval.plugins.stt.open_asr:STTEvalPlugin"
tts_eval = "voicelearn_eval.plugins.tts.quality:TTSEvalPlugin"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
```
