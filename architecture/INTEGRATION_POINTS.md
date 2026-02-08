# Integration Points

How the evaluation system connects to upstream tools and external services.

## 1. EleutherAI lm-evaluation-harness

**Repository:** https://github.com/EleutherAI/lm-evaluation-harness
**Integration type:** Python library + subprocess fallback

### Python API (preferred)

```python
import lm_eval

results = lm_eval.simple_evaluate(
    model="hf",
    model_args="pretrained=Qwen/Qwen2.5-3B-Instruct,dtype=float16",
    tasks=["mmlu_high_school_biology", "arc_challenge", "gsm8k"],
    batch_size=8,
    device="cuda:0",
    num_fewshot=5,
    log_samples=True,
)

# results["results"] contains per-task metrics:
# {"mmlu_high_school_biology": {"acc": 0.78, "acc_norm": 0.82, ...}}
```

### Subprocess Mode (for isolation)

```python
import subprocess, json

cmd = [
    "lm_eval",
    "--model", "hf",
    "--model_args", f"pretrained={model_path},dtype=float16",
    "--tasks", ",".join(task_names),
    "--batch_size", "8",
    "--device", "cuda:0",
    "--output_path", str(output_dir),
    "--log_samples",
]
result = subprocess.run(cmd, capture_output=True, text=True)

# Parse JSON results from output_dir/results.json
with open(output_dir / "results.json") as f:
    raw_results = json.load(f)
```

### Model Backends Supported

| Backend | `--model` arg | Use Case |
|---------|-------------|----------|
| HuggingFace Transformers | `hf` | Standard HF models |
| vLLM | `vllm` | High-throughput server evaluation |
| GGUF via llama.cpp | `hf` with GGUF path | On-device candidates |
| OpenAI-compatible API | `local-completions` | Cloud/API models |

### Custom Task Definitions

Education-specific tasks are defined as YAML files following lm-eval-harness format:

```yaml
# test_sets/llm/custom_tasks/edu_tutoring_quality.yaml
task: edu_tutoring_quality
dataset_path: local  # or HuggingFace dataset
dataset_name: tutoring_scenarios
output_type: generate_until
doc_to_text: "{{prompt}}"
doc_to_target: "{{expected}}"
metric_list:
  - metric: bleu
  - metric: rouge
filter_list:
  - name: strip
    filter:
      - function: strip
```

### Result Mapping

lm-eval-harness metrics map to our normalized scores:

| lm-eval-harness metric | Our metric | Normalization |
|------------------------|------------|---------------|
| `acc` | `accuracy` | multiply by 100 |
| `acc_norm` | `accuracy_normalized` | multiply by 100 |
| `exact_match` | `exact_match` | multiply by 100 |
| `f1` | `f1` | multiply by 100 |
| `bleu` | `bleu` | already 0-100 |

## 2. HuggingFace Open ASR Leaderboard

**Repository:** https://github.com/huggingface/open_asr_leaderboard
**Integration type:** Python library (transformers + datasets)

### Evaluation Pipeline

```python
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import jiwer

# Load model
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch.float16)
processor = AutoProcessor.from_pretrained(model_id)
pipe = pipeline("automatic-speech-recognition", model=model, processor=processor)

# Load dataset
dataset = load_dataset("librispeech_asr", "clean", split="test")

# Run evaluation
predictions = []
references = []
for sample in dataset:
    result = pipe(sample["audio"]["array"], return_timestamps=True)
    predictions.append(result["text"])
    references.append(sample["text"])

# Compute WER
wer = jiwer.wer(references, predictions)
cer = jiwer.cer(references, predictions)
```

### Datasets Used

| Dataset | HuggingFace ID | Split |
|---------|---------------|-------|
| LibriSpeech Clean | `librispeech_asr` | `test.clean` |
| LibriSpeech Other | `librispeech_asr` | `test.other` |
| Common Voice | `mozilla-foundation/common_voice_16_1` | `test` |
| TED-LIUM | `LIUM/tedlium` | `test` |
| GigaSpeech | `speechcolab/gigaspeech` | `test` |

### Custom Educational Vocabulary

Custom domain-specific test sets stored as JSON with audio file references:

```json
{
  "domain": "biology",
  "education_tier": "highschool",
  "items": [
    {
      "audio_path": "test_sets/stt/audio/biology_hs_001.wav",
      "transcript": "The mitochondria is the powerhouse of the cell",
      "terms": ["mitochondria"],
      "difficulty": "medium"
    }
  ]
}
```

Audio can be real recordings or synthesized using a reference TTS model.

## 3. Picovoice STT Benchmark

**Repository:** https://github.com/Picovoice/speech-to-text-benchmark
**Integration type:** Methodology adoption + custom implementation

We adopt Picovoice's metrics rather than wrapping their code directly:

- **Core-Hour:** CPU hours to process 1 hour of audio
- **Word Emission Latency:** Time from word spoken to transcription emitted (streaming only)
- **Model Size:** Aggregate disk footprint

### Implementation

```python
import time
import psutil

def measure_stt_performance(model, audio_samples):
    """Measure STT performance metrics following Picovoice methodology."""
    total_audio_duration = 0
    total_processing_time = 0
    peak_memory = 0

    for audio in audio_samples:
        audio_duration = len(audio) / sample_rate
        total_audio_duration += audio_duration

        process = psutil.Process()
        mem_before = process.memory_info().rss

        start = time.perf_counter()
        transcription = model.transcribe(audio)
        elapsed = time.perf_counter() - start

        total_processing_time += elapsed
        mem_after = process.memory_info().rss
        peak_memory = max(peak_memory, mem_after - mem_before)

    rtfx = total_audio_duration / total_processing_time
    core_hours = total_processing_time / 3600

    return {
        "rtfx": rtfx,
        "core_hours_per_audio_hour": core_hours / (total_audio_duration / 3600),
        "peak_memory_mb": peak_memory / 1024 / 1024,
    }
```

## 4. UTMOS (Automated MOS Scoring)

**Repository:** https://github.com/sarulab-speech/UTMOS22
**Integration type:** Python library

### Setup

```bash
pip install torch torchaudio
# UTMOS model is loaded from a HuggingFace checkpoint
```

### Evaluation

```python
import torch
import torchaudio

# Load UTMOS predictor
predictor = torch.hub.load("sarulab-speech/UTMOS22", "utmos22_strong", trust_repo=True)

def score_tts_quality(audio_path: str) -> float:
    """Score TTS audio quality using UTMOS (1-5 scale)."""
    waveform, sr = torchaudio.load(audio_path)
    if sr != 16000:
        waveform = torchaudio.transforms.Resample(sr, 16000)(waveform)

    with torch.no_grad():
        score = predictor(waveform, sr=16000)

    return score.item()  # Float between 1.0 and 5.0
```

## 5. WVMOS (Wav2Vec MOS)

**Repository:** https://github.com/AndreevP/wvmos
**Integration type:** Python library

### Evaluation

```python
from wvmos import get_wvmos

model = get_wvmos(cuda=True)

def score_wvmos(audio_path: str) -> float:
    """Score TTS audio quality using WVMOS (1-5 scale)."""
    score = model.calculate_one(audio_path)
    return score  # Float between 1.0 and 5.0
```

### Combined MOS Scoring

```python
def combined_mos(audio_path: str) -> dict:
    """Average UTMOS and WVMOS for more robust quality assessment."""
    utmos = score_tts_quality(audio_path)
    wvmos = score_wvmos(audio_path)
    return {
        "mos_utmos": utmos,
        "mos_wvmos": wvmos,
        "mos_average": (utmos + wvmos) / 2,
    }
```

## 6. Pronunciation Evaluation

**Tool:** Montreal Forced Aligner (MFA)
**Repository:** https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner

### Pipeline

```python
def evaluate_pronunciation(audio_path, expected_text, expected_phonemes):
    """Evaluate pronunciation accuracy using forced alignment.

    1. Run forced alignment on generated audio
    2. Extract phoneme sequence from alignment
    3. Compare to expected pronunciation
    4. Calculate Phoneme Error Rate (PER)
    """
    # Step 1: Forced alignment
    alignment = run_mfa(audio_path, expected_text)

    # Step 2: Extract phonemes
    actual_phonemes = extract_phonemes(alignment)

    # Step 3: Compare
    per = phoneme_error_rate(expected_phonemes, actual_phonemes)

    return {
        "pronunciation_correct": per < 0.15,  # 15% PER threshold
        "phoneme_error_rate": per,
        "expected_phonemes": expected_phonemes,
        "actual_phonemes": actual_phonemes,
    }
```

## 7. Intelligibility Round-Trip

Uses a high-quality STT model (Whisper Large V3) to measure TTS intelligibility:

```python
import jiwer

def evaluate_intelligibility(tts_model, stt_model, test_sentences):
    """Synthesize speech, then transcribe it, then compare.

    A low WER means the TTS is producing highly intelligible speech.
    """
    results = []
    for sentence in test_sentences:
        # Generate audio
        audio = tts_model.synthesize(sentence)

        # Transcribe with reference STT
        transcription = stt_model.transcribe(audio)

        # Compare
        wer = jiwer.wer(sentence.lower(), transcription.lower())
        results.append({"text": sentence, "transcription": transcription, "wer": wer})

    avg_wer = sum(r["wer"] for r in results) / len(results)
    return {"intelligibility_wer": avg_wer, "details": results}
```

## 8. HuggingFace Hub (Model Discovery)

**Library:** `huggingface_hub`
**Integration type:** Python library for model search and metadata

```python
from huggingface_hub import HfApi

api = HfApi()

def search_models(query: str, model_type: str) -> list[dict]:
    """Search HuggingFace Hub for models."""
    pipeline_tag = {
        "llm": "text-generation",
        "stt": "automatic-speech-recognition",
        "tts": "text-to-speech",
    }.get(model_type)

    models = api.list_models(
        search=query,
        pipeline_tag=pipeline_tag,
        sort="downloads",
        limit=20,
    )

    return [
        {
            "repo_id": m.modelId,
            "name": m.modelId.split("/")[-1],
            "downloads": m.downloads,
            "likes": m.likes,
            "tags": m.tags,
            "pipeline_tag": m.pipeline_tag,
        }
        for m in models
    ]

def get_model_metadata(repo_id: str) -> dict:
    """Fetch detailed model metadata from HuggingFace."""
    info = api.model_info(repo_id)
    return {
        "repo_id": info.modelId,
        "parameters": extract_param_count(info),
        "model_size": sum(s.size for s in (info.siblings or [])),
        "license": info.cardData.get("license") if info.cardData else None,
        "languages": info.cardData.get("language") if info.cardData else None,
        "tags": info.tags,
    }
```

## 9. MTEB (Embeddings Evaluation)

**Repository:** https://github.com/embeddings-benchmark/mteb
**Integration type:** Python library

```python
import mteb

def evaluate_embeddings(model_name, tasks=None):
    """Evaluate embedding model using MTEB benchmark."""
    model = mteb.get_model(model_name)
    tasks = tasks or ["STS22", "AmazonReviewsClassification", "ArguAna"]
    evaluation = mteb.MTEB(tasks=tasks)
    results = evaluation.run(model)
    return results
```

## 10. CI/CD Integration (GitHub Actions)

### Triggered Evaluation

```yaml
# .github/workflows/evaluate.yml
name: Model Evaluation

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Model ID (HuggingFace repo or local path)'
        required: true
      suite:
        description: 'Benchmark suite'
        default: 'education_focus'
  schedule:
    - cron: '0 0 * * SUN'  # Weekly Sunday midnight

jobs:
  evaluate:
    runs-on: [self-hosted, gpu]
    steps:
      - uses: actions/checkout@v4

      - name: Install
        run: pip install edu-voice-ai-eval

      - name: Run evaluation
        run: |
          voicelearn-eval run \
            --model ${{ inputs.model || 'all-registered' }} \
            --suite ${{ inputs.suite }} \
            --ci \
            --output results/
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: results/
```

### New Model Detection

```yaml
# .github/workflows/new_model.yml
name: New Model Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check for new models
        run: |
          voicelearn-eval model check-new \
            --families qwen,llama,mistral,whisper,piper \
            --since 7d
        # Triggers evaluate.yml if new models found
```

## Dependency Summary

| Integration | Python Package | Version | Required |
|-------------|---------------|---------|----------|
| lm-evaluation-harness | `lm-eval` | >=0.4 | Yes (LLM) |
| HuggingFace | `transformers`, `datasets`, `huggingface_hub` | latest | Yes |
| WER computation | `jiwer` | >=3.0 | Yes (STT) |
| UTMOS | `torch`, `torchaudio` | >=2.0 | Yes (TTS) |
| WVMOS | `wvmos` | latest | Yes (TTS) |
| MTEB | `mteb` | >=1.0 | Optional (Embeddings) |
| Forced alignment | `montreal-forced-aligner` | >=3.0 | Optional (pronunciation) |
| FastAPI | `fastapi`, `uvicorn` | latest | Yes (API) |
| Click | `click` | >=8.0 | Yes (CLI) |
| pluggy | `pluggy` | >=1.0 | Yes (plugins) |
