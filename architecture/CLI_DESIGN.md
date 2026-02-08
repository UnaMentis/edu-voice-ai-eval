# CLI Design

The CLI is the primary interface for automation, CI/CD, and power users. Built with [Click](https://click.palletsprojects.com/) for rich subcommand support, auto-generated help, and clean argument parsing.

## Installation

```bash
pip install edu-voice-ai-eval

# Verify
voicelearn-eval --version
voicelearn-eval --help
```

Or run as a module:
```bash
python -m voicelearn_eval --help
```

## Command Structure

```
voicelearn-eval
├── run           # Run evaluations
├── list          # List resources (models, benchmarks, runs, etc.)
├── compare       # Compare models
├── grade         # Grade-level assessment
├── export        # Export results
├── import        # Import results
├── serve         # Start API server + web dashboard
├── model         # Model registry management
├── suite         # Benchmark suite management
├── plugin        # Plugin management
└── schedule      # Evaluation scheduling
```

## Commands

### `voicelearn-eval run`

Run an evaluation of a model against a benchmark suite.

```
voicelearn-eval run [OPTIONS]

Options:
  --model TEXT        Model ID, HuggingFace repo, or local path (required, repeatable)
  --suite TEXT        Predefined suite name (required unless --benchmark specified)
  --benchmark TEXT    Specific benchmark ID (repeatable, alternative to --suite)
  --config PATH      YAML configuration file
  --gpu TEXT          GPU device: "cuda:0", "mps", "cpu" (default: auto-detect)
  --batch-size INT    Batch size for evaluation (default: from config)
  --output PATH      Output directory for results
  --format TEXT       Output format: json, csv, vlef (default: json)
  --ci                CI mode: non-zero exit code on failure, structured output
  --timeout INT       Timeout in seconds per benchmark (default: 3600)
  --quiet             Suppress progress output
  --priority INT      Queue priority: 0=low, 5=normal, 10=urgent (default: 5)
```

**Examples:**

```bash
# Quick evaluation with a predefined suite
voicelearn-eval run --model Qwen/Qwen2.5-3B-Instruct --suite quick_scan

# Full education evaluation on GPU
voicelearn-eval run --model Qwen/Qwen2.5-3B-Instruct --suite education_focus --gpu cuda:0

# Evaluate a local GGUF model
voicelearn-eval run --model /path/to/model.gguf --suite education_focus

# Evaluate an API endpoint
voicelearn-eval run --model api:gpt-4o --suite education_focus

# Run specific benchmarks
voicelearn-eval run --model Qwen/Qwen2.5-3B-Instruct \
  --benchmark edu_tier1_gsm8k \
  --benchmark edu_tier2_arc_challenge

# CI mode: fail if score below threshold
voicelearn-eval run --model my-finetuned-model --suite education_focus --ci

# Multiple models in one run
voicelearn-eval run \
  --model Qwen/Qwen2.5-3B-Instruct \
  --model mistralai/Ministral-3B-Instruct \
  --suite quick_scan
```

### `voicelearn-eval list`

List resources in the system.

```
voicelearn-eval list [RESOURCE]

Resources:
  models       List registered models
  benchmarks   List available benchmarks (from all plugins)
  plugins      List loaded plugins with status
  runs         List past evaluation runs
  suites       List predefined benchmark suites
```

**Options for `list runs`:**
```
  --status TEXT       Filter by status: pending, running, completed, failed
  --model TEXT        Filter by model ID
  --suite TEXT        Filter by suite name
  --limit INT         Max results (default: 20)
  --format TEXT       Output format: table, json (default: table)
```

**Examples:**
```bash
voicelearn-eval list models
voicelearn-eval list benchmarks --type llm
voicelearn-eval list runs --status completed --limit 10
voicelearn-eval list suites
voicelearn-eval list plugins
```

### `voicelearn-eval compare`

Compare evaluation results across models.

```
voicelearn-eval compare [OPTIONS]

Options:
  --models TEXT       Model IDs to compare (2-5, space-separated, required)
  --benchmarks TEXT   Benchmark IDs to compare on (space-separated, optional)
  --suite TEXT        Compare using results from this suite
  --format TEXT       Output format: table, json, csv (default: table)
  --output PATH       Save comparison to file
```

**Examples:**
```bash
# Compare two models across all shared benchmarks
voicelearn-eval compare --models "Qwen2.5-3B Ministral-3B"

# Compare on specific benchmarks
voicelearn-eval compare \
  --models "Qwen2.5-3B Ministral-3B Phi-3-Mini" \
  --benchmarks "edu_tier1_gsm8k edu_tier2_arc_challenge"

# Export comparison as JSON
voicelearn-eval compare --models "Qwen2.5-3B Ministral-3B" --format json --output comparison.json
```

**Table output:**
```
Model Comparison: education_focus suite
┌─────────────────┬──────────┬──────────────┬──────────────┬──────────┐
│ Benchmark       │ Qwen 2.5 │ Ministral-3B │ Phi-3 Mini   │ Best     │
├─────────────────┼──────────┼──────────────┼──────────────┼──────────┤
│ Tier 1: GSM8K   │ 82.3     │ 78.1         │ 45.2         │ Qwen 2.5 │
│ Tier 2: ARC-C   │ 71.5     │ 68.9         │ 38.7         │ Qwen 2.5 │
│ Tier 3: MATH    │ 45.8     │ 42.1         │ 18.3         │ Qwen 2.5 │
│ TruthfulQA      │ 65.2     │ 71.3         │ 52.8         │ Mini-3B  │
├─────────────────┼──────────┼──────────────┼──────────────┼──────────┤
│ Overall         │ 66.2     │ 65.1         │ 38.8         │ Qwen 2.5 │
│ Max Edu Tier    │ Tier 2   │ Tier 1       │ (none)       │          │
└─────────────────┴──────────┴──────────────┴──────────────┴──────────┘
```

### `voicelearn-eval grade`

Assess a model's education grade-level capability.

```
voicelearn-eval grade [OPTIONS]

Options:
  --model TEXT        Model ID (required)
  --threshold FLOAT   Passing score threshold, 0.0-1.0 (default: 0.70)
  --run TEXT          Use results from a specific run (default: latest)
  --format TEXT       Output format: table, json (default: table)
```

**Example output:**
```
Grade-Level Assessment: Qwen 2.5 3B Instruct
Threshold: 70%

┌─────────────────────────┬───────┬────────┬─────────────────────────────┐
│ Tier                    │ Score │ Status │ Key Benchmarks              │
├─────────────────────────┼───────┼────────┼─────────────────────────────┤
│ Tier 1: Elementary      │ 85.2% │ PASS   │ GSM8K: 82%, ARC-E: 88%     │
│ Tier 2: High School     │ 72.1% │ PASS   │ ARC-C: 71%, MMLU-HS: 73%   │
│ Tier 3: Undergraduate   │ 48.3% │ FAIL   │ MATH: 45%, MMLU-Pro: 51%   │
│ Tier 4: Graduate        │ 22.7% │ FAIL   │ GPQA: 23%, MMLU-Pro: 22%   │
└─────────────────────────┴───────┴────────┴─────────────────────────────┘

Maximum Passing Tier: HIGH SCHOOL (Tier 2)
Recommendation: Suitable for tutoring through high school level content.
```

### `voicelearn-eval export`

Export evaluation results.

```
voicelearn-eval export [OPTIONS]

Options:
  --run TEXT          Run ID to export (required unless --all)
  --all               Export all results
  --model TEXT        Export all results for a model
  --format TEXT       Export format: json, csv, vlef (default: vlef)
  --output PATH       Output file path (required)
```

**Examples:**
```bash
# Export a single run as VLEF
voicelearn-eval export --run run_abc123 --format vlef --output results.vlef.json

# Export all results for a model as CSV
voicelearn-eval export --model Qwen2.5-3B --format csv --output qwen_results.csv

# Export everything as VLEF for sharing
voicelearn-eval export --all --format vlef --output full_export.vlef.json
```

### `voicelearn-eval import`

Import results from a VLEF file.

```
voicelearn-eval import [OPTIONS]

Options:
  --file PATH        VLEF file to import (required)
  --merge             Merge with existing results (default: skip duplicates)
  --overwrite         Overwrite existing results on conflict
```

### `voicelearn-eval serve`

Start the API server and web dashboard.

```
voicelearn-eval serve [OPTIONS]

Options:
  --port INT          API server port (default: 8790)
  --web-port INT      Web dashboard port (default: 3001)
  --host TEXT         Bind host (default: 127.0.0.1)
  --no-web            API server only, no web dashboard
  --reload            Enable auto-reload for development
  --db PATH           Database path (default: ~/.voicelearn-eval/data.db)
```

**Examples:**
```bash
# Start with defaults
voicelearn-eval serve
# API: http://localhost:8790
# Web: http://localhost:3001

# Production mode
voicelearn-eval serve --host 0.0.0.0 --port 8790 --web-port 3001

# API only (no web UI)
voicelearn-eval serve --no-web --port 8790
```

### `voicelearn-eval model`

Manage the model registry.

```
voicelearn-eval model [SUBCOMMAND]

Subcommands:
  add          Register a model manually
  import-hf    Import a model from HuggingFace
  remove       Remove a model from registry
  info         Show model details
```

**Examples:**
```bash
# Import from HuggingFace
voicelearn-eval model import-hf Qwen/Qwen2.5-3B-Instruct --type llm --target server

# Register a local model
voicelearn-eval model add \
  --name "My Fine-tuned Model" \
  --type llm \
  --source local \
  --path /models/my-model.gguf \
  --params 3.0 \
  --quantization Q4_K_M

# Register an API endpoint
voicelearn-eval model add \
  --name "Claude 3.5 Sonnet" \
  --type llm \
  --source api \
  --api-url https://api.anthropic.com/v1 \
  --api-key-env ANTHROPIC_API_KEY \
  --target cloud-api \
  --reference  # Mark as reference model
```

### `voicelearn-eval suite`

Manage benchmark suites.

```
voicelearn-eval suite [SUBCOMMAND]

Subcommands:
  list         List available suites
  info         Show suite details and tasks
  create       Create a custom suite from YAML
```

### `voicelearn-eval plugin`

Manage evaluation plugins.

```
voicelearn-eval plugin [SUBCOMMAND]

Subcommands:
  list         List discovered plugins
  info         Show plugin details and supported benchmarks
```

### `voicelearn-eval schedule`

Manage recurring evaluations.

```
voicelearn-eval schedule [SUBCOMMAND]

Subcommands:
  list         List active schedules
  create       Create a new schedule
  remove       Remove a schedule
  run-now      Trigger a scheduled evaluation immediately
```

**Example:**
```bash
# Weekly evaluation of all LLM models
voicelearn-eval schedule create \
  --name "Weekly LLM Eval" \
  --suite education_focus \
  --model-type llm \
  --cron "0 0 * * SUN"
```

## Predefined Suites

| Suite | Models | Benchmarks | Est. Duration |
|-------|--------|------------|---------------|
| `quick_scan` | LLM | MMLU (subset), ARC Easy, GSM8K | ~5 min |
| `education_focus` | LLM | All 4 tiers, TruthfulQA, HellaSwag | ~30 min |
| `full_llm` | LLM | All LLM benchmarks including MATH, GPQA | ~2 hrs |
| `stt_standard` | STT | LibriSpeech, CommonVoice, TED-LIUM | ~15 min |
| `stt_education` | STT | Standard + educational vocabulary | ~20 min |
| `tts_quality` | TTS | MOS, pronunciation, intelligibility | ~10 min |
| `on_device` | All | Quick quality + performance metrics | ~15 min |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Evaluation completed but score below CI threshold |
| 2 | Evaluation failed (error during execution) |
| 3 | Invalid arguments or configuration |
| 4 | Model not found or inaccessible |
| 5 | Plugin error (missing plugin for requested benchmark) |

## Configuration File

The `--config` option accepts YAML configuration:

```yaml
# configs/education_focus.yaml
suite: education_focus
gpu: auto
batch_size: 8
timeout_per_benchmark: 3600

# CI thresholds (only used with --ci flag)
ci:
  min_overall_score: 60
  min_tier1_score: 70
  min_tier2_score: 50
  fail_on_regression: true
  regression_threshold: 0.10  # 10% drop = failure

# Output
output:
  format: json
  save_raw_outputs: true
  save_samples: true  # Save TTS audio samples
```
