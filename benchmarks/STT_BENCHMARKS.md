# STT Evaluation Benchmarks

Speech-to-text model evaluation methodology, covering standard accuracy benchmarks, educational domain testing, and on-device performance assessment.

## Primary Metric: Word Error Rate (WER)

WER is the standard STT accuracy metric:

```
WER = (Substitutions + Insertions + Deletions) / Total Words in Reference
```

A WER of 5% means 5 out of every 100 words are wrong. Lower is better.

Computed using [jiwer](https://github.com/jitsi/jiwer), which handles text normalization (case, punctuation) before comparison.

## Standard Datasets

Following the HuggingFace Open ASR Leaderboard methodology:

| Dataset | Domain | Samples | Duration | Why It Matters |
|---------|--------|---------|----------|---------------|
| LibriSpeech Clean | Audiobook narration | 2,620 | 5.4h | Baseline accuracy (clean audio) |
| LibriSpeech Other | Audiobook, noisier | 2,939 | 5.3h | Robustness to audio quality |
| Common Voice EN | Crowdsourced | ~16K | ~24h | Accent diversity |
| TED-LIUM | TED talks | 1,155 | 2.6h | Educational/lecture-style speech |
| GigaSpeech | Podcast, YouTube | 40K+ | ~40h | Real-world multi-domain |
| AMI | Meeting recordings | ~3K | ~9h | Multi-speaker, noisy environments |

## Educational Domain Testing

Standard benchmarks don't test whether a model can transcribe academic vocabulary. Our custom domain test sets fill this gap.

### Educational Vocabulary Test Sets

Organized by education tier, matching the LLM grade-level system:

**Tier 1: Elementary (Grades 5-8)**
```json
{
  "tier": "elementary",
  "terms": [
    "photosynthesis", "ecosystem", "denominator", "fraction",
    "evaporation", "condensation", "vertebrate", "invertebrate",
    "peninsula", "continent", "democracy", "civilization"
  ]
}
```

**Tier 2: High School (Grades 9-12)**
```json
{
  "tier": "highschool",
  "terms": [
    "mitochondria", "stoichiometry", "logarithm", "polynomial",
    "electromagnetic", "photosynthesis", "homeostasis", "entropy",
    "Renaissance", "Enlightenment", "mercantilism", "imperialism"
  ]
}
```

**Tier 3: Undergraduate (College)**
```json
{
  "tier": "undergrad",
  "terms": [
    "epigenetics", "eigenvalue", "Keynesian", "thermodynamics",
    "neurotransmitter", "phosphorylation", "isomorphism",
    "phenomenology", "epistemology", "hermeneutics"
  ]
}
```

**Tier 4: Graduate (PhD)**
```json
{
  "tier": "grad",
  "terms": [
    "angiogenesis", "Lagrangian mechanics", "heteroscedasticity",
    "nucleophilic substitution", "Bayesian inference",
    "topological manifold", "ontological commitment"
  ]
}
```

### How Domain Test Sets Are Created

1. **Compile term lists** from textbooks and curricula at each education level
2. **Generate audio** using a high-quality reference TTS model (e.g., ElevenLabs or Chatterbox)
3. **Embed terms in sentences** to test contextual recognition: "The mitochondria is often called the powerhouse of the cell"
4. **Include isolated terms** to test standalone recognition: just the word "stoichiometry"
5. **Multiple speakers** where possible (different TTS voices or real recordings)

### Domain WER Calculation

```python
def calculate_domain_wer(results: list[dict], domain: str) -> float:
    """Calculate WER specifically for educational domain terms.

    Only counts errors on the target terms, not surrounding words.
    """
    domain_results = [r for r in results if r["domain"] == domain]
    total_terms = len(domain_results)
    correct_terms = sum(1 for r in domain_results if r["term_correct"])
    return 1.0 - (correct_terms / total_terms) if total_terms > 0 else 1.0
```

## Performance Metrics

### RTFx (Real-Time Factor)

How many seconds of audio the model processes per second of compute:
- RTFx = 1.0: Processes audio at real-time speed
- RTFx = 10.0: 10x faster than real-time
- RTFx = 0.5: 2x slower than real-time (not suitable for streaming)

For voice-based tutoring, RTFx must be > 1.0 for real-time interaction.

### Latency Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| TTFB (Time to First Byte) | Time from audio submission to first transcription output | <300ms |
| Total latency | Time to complete transcription of a segment | <500ms for 5s audio |
| Word Emission Latency | Time from word spoken to word transcribed (streaming) | <200ms |

### On-Device Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Model size | Disk footprint | <500MB |
| Peak memory | RAM during inference | <1GB |
| CPU/GPU load | Compute utilization | Reasonable on mobile SoC |
| Battery impact | Power consumption estimate | <5% per hour |

## Predefined Suites

### `stt_standard`
Purpose: Standard accuracy benchmark
Datasets: LibriSpeech (clean + other), Common Voice, TED-LIUM
Duration: ~15 minutes

### `stt_education`
Purpose: Standard + educational domain accuracy
Datasets: Standard + all four tier vocabulary sets
Duration: ~20 minutes

### `stt_on_device`
Purpose: On-device feasibility assessment
Datasets: LibriSpeech Clean + educational vocabulary (reduced)
Additional: RTFx, memory, model size, latency
Duration: ~10 minutes

## Key Models to Track

### On-Device Candidates

| Model | Params | Size | Notes |
|-------|--------|------|-------|
| Moonshine Base | 27M | ~30MB | Smallest viable STT |
| Moonshine | 240M | ~250MB | Best on-device accuracy/size |
| Whisper Tiny | 39M | ~75MB | Baseline Whisper |
| Whisper Small | 244M | ~460MB | Good accuracy for size |
| Vosk (small models) | Varies | ~50MB | CPU-friendly, offline |

### Server Candidates

| Model | Params | WER (LS clean) | Notes |
|-------|--------|----------------|-------|
| Canary Qwen 2.5B | 2.5B | ~5.6% | Top of Open ASR Leaderboard |
| Whisper Large V3 Turbo | 809M | ~5-7% | Best multilingual |
| NVIDIA Parakeet TDT v3 | 0.6-1.1B | Very low | Speed + accuracy |
| Granite Speech 3.3 | 8B | ~5.85% | IBM enterprise |

### Current UnaMentis Models

| Platform | Primary | Fallback |
|----------|---------|----------|
| iOS | Deepgram Nova-3 (streaming) | Apple Speech (on-device) |
| Android | Deepgram Nova-3 (streaming) | (planned) |

## Evaluation Output

Each STT evaluation produces:

```json
{
  "model": "openai/whisper-large-v3-turbo",
  "overall_wer": 0.042,
  "dataset_results": {
    "librispeech_clean": { "wer": 0.021, "cer": 0.008, "samples": 2620 },
    "librispeech_other": { "wer": 0.048, "cer": 0.019, "samples": 2939 },
    "common_voice": { "wer": 0.052, "cer": 0.021, "samples": 16000 },
    "edu_vocabulary": { "wer": 0.073, "cer": 0.031, "samples": 800 }
  },
  "domain_wer": {
    "biology": 0.068,
    "physics": 0.051,
    "math": 0.082,
    "cs": 0.032,
    "history": 0.045,
    "chemistry": 0.079
  },
  "performance": {
    "rtfx": 12.5,
    "latency_ms": 150,
    "model_size_mb": 3100,
    "peak_memory_mb": 4200
  },
  "on_device_feasible": false,
  "feasibility_notes": "Model exceeds 500MB on-device target"
}
```
