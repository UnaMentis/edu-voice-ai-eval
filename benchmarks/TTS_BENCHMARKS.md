# TTS Evaluation Benchmarks

Text-to-speech model evaluation methodology, covering automated quality scoring, pronunciation accuracy, prosody analysis, and intelligibility testing.

## The Challenge

TTS quality is inherently subjective. "Can I listen to this for 90 minutes of tutoring?" is a human judgment. Our approach combines multiple automated metrics that correlate well with human perception, plus education-specific tests that standard benchmarks miss.

## Quality Metrics

### MOS (Mean Opinion Score) via UTMOS + WVMOS

**Scale:** 1.0 (bad) to 5.0 (excellent)
**Method:** Average of UTMOS and WVMOS predictions for robustness

| Score Range | Quality Level | Suitability for Tutoring |
|-------------|--------------|-------------------------|
| 4.5 - 5.0 | Excellent, near-human | Ideal for extended sessions |
| 4.0 - 4.5 | Very good | Good for tutoring |
| 3.5 - 4.0 | Good | Acceptable, some listener fatigue |
| 3.0 - 3.5 | Fair | Noticeable artifacts, short sessions only |
| < 3.0 | Poor | Not suitable for educational use |

**Test sentences:** A diverse set of 100 sentences covering:
- Short factual statements (5-10 words)
- Long explanations (30-50 words)
- Questions (interrogative intonation)
- Lists and enumerations
- Technical terminology
- Emotional content (encouragement, correction)

### Intelligibility via STT Round-Trip

**Method:** Synthesize speech, then transcribe it with a reference STT model (Whisper Large V3), then compare to original text.

```
Input text -> TTS model -> Audio -> Whisper V3 -> Transcribed text -> WER
```

A low WER means the speech is highly intelligible. Target: WER < 3%.

**Why this matters for education:** If a TTS model says "stoichiometry" but it sounds like "stoy-kee-ometry" and Whisper transcribes it as "stochometry", students will learn the wrong pronunciation.

### Pronunciation Accuracy

**Method:** Evaluate how correctly the model pronounces difficult educational terms using forced alignment and phoneme comparison.

**Test set:** 200+ educational terms organized by difficulty:

| Category | Example Terms | Count |
|----------|--------------|-------|
| Scientific names | mitochondria, photosynthesis, chromatography | 40 |
| Mathematical terms | polynomial, asymptote, Pythagorean, eigenvalue | 30 |
| Historical names | Charlemagne, Machiavelli, Tocqueville | 25 |
| Chemical terms | stoichiometry, electronegativity, isomer | 30 |
| Foreign-origin terms | renaissance, bourgeoisie, zeitgeist | 25 |
| Medical/Bio terms | angiogenesis, epigenetics, neuroplasticity | 25 |
| Physics terms | Lagrangian, Hamiltonian, Schrodinger | 25 |

**Scoring:**
- Each term is scored as correct or incorrect
- Pronunciation accuracy = correct / total
- Target: > 90% accuracy

**Automated scoring pipeline:**
1. Synthesize each term in a carrier sentence: "The word is [term]"
2. Run Montreal Forced Aligner to extract phoneme sequence
3. Compare extracted phonemes to expected pronunciation (from dictionary or manual annotation)
4. Calculate Phoneme Error Rate (PER) per term
5. Term is "correct" if PER < 15%

### Prosody Analysis

For extended listening (60-90+ minute tutoring sessions), monotonous speech causes listener fatigue.

**Metrics:**

| Metric | What It Measures | How |
|--------|-----------------|-----|
| Pitch range (Hz) | Intonation variety | F0 extraction via CREPE or librosa |
| Pitch variation (std dev) | Expressiveness | Standard deviation of F0 |
| Speaking rate variation | Natural pacing | Syllables per second variance |
| Pause distribution | Natural rhythm | Silence segment analysis |
| Energy variation | Dynamic range | RMS energy standard deviation |

**Prosody score:** Composite of the above metrics, normalized against human speech baselines. A perfectly monotone voice scores near 0; natural human speech scores near 1.0.

## Test Sentence Categories

### Standard Evaluation Sentences

```text
# Short declarative
"Water boils at one hundred degrees Celsius."
"The speed of light is approximately three hundred million meters per second."

# Long explanation
"The mitochondria is often called the powerhouse of the cell because it generates
most of the cell's supply of adenosine triphosphate, which is used as a source
of chemical energy."

# Question
"Can you explain why the sky appears blue during the daytime?"

# Encouragement
"That's a great observation! You're really starting to understand how
photosynthesis works."

# Correction
"Not quite. Remember that the formula requires you to square the hypotenuse,
not just multiply it by two."

# List/enumeration
"The three branches of government are: the legislative branch, which makes laws;
the executive branch, which enforces laws; and the judicial branch, which
interprets laws."
```

### Pronunciation Challenge Sentences

```text
# Science
"Stoichiometry is the study of quantitative relationships in chemical reactions."
"The Krebs cycle, also known as the citric acid cycle, occurs in the mitochondrial matrix."

# Math
"Euler's identity connects five fundamental mathematical constants: e, i, pi, one, and zero."
"The Pythagorean theorem states that the square of the hypotenuse equals the sum of the squares."

# History
"Charlemagne united much of Western Europe during the Carolingian Renaissance."
"Niccolò Machiavelli wrote The Prince during the Italian Renaissance."

# Technical
"The Schrödinger equation describes how the quantum state evolves over time."
"Bernoulli's principle explains the relationship between fluid speed and pressure."
```

## On-Device TTS Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| TTFB (ms) | Time to first audio byte | <200ms |
| RTF | Real-time factor (synthesis speed) | <1.0 (real-time or faster) |
| Model size (MB) | Disk footprint | <500MB |
| Peak memory (MB) | RAM during synthesis | <500MB |
| Audio quality (kHz) | Output sample rate | >=16kHz (24kHz preferred) |

## Predefined Suites

### `tts_quality`
Purpose: Comprehensive quality assessment
Tests: MOS, intelligibility, pronunciation, prosody
Sentences: 100 standard + 200 pronunciation challenge
Duration: ~10 minutes

### `tts_quick`
Purpose: Fast quality check
Tests: MOS on 20 sentences, intelligibility on 10
Duration: ~3 minutes

### `tts_on_device`
Purpose: On-device feasibility
Tests: Quality (reduced set) + performance metrics
Duration: ~5 minutes

## Key Models to Track

### On-Device Candidates

| Model | Params | Size | MOS (est) | TTFB | Notes |
|-------|--------|------|-----------|------|-------|
| Kokoro-82M | 82M | ~100MB | ~3.8 | <300ms | Smallest, fastest |
| NeuTTS Air | 0.5B | ~500MB | ~4.5 | Real-time | Near-human, GGUF |
| Orpheus-150M | 150M | ~200MB | ~3.5 | Fast | Multiple sizes available |

### Server Candidates

| Model | Params | MOS (est) | TTFB | Notes |
|-------|--------|-----------|------|-------|
| Chatterbox | 0.5B | ~4.1 | Very fast | Emotion control, MIT |
| Chatterbox Turbo | 0.5B | ~4.0 | 1-step | Fastest quality TTS |
| F5-TTS | Medium | ~4.5 | Medium | Best naturalness |
| CosyVoice2-0.5B | 0.5B | 5.53 | 150ms | Low latency + quality |
| Higgs Audio V2 | ~3B | ~4.7 | Medium | Best emotional range |
| XTTS-v2 | Medium | ~4.0 | Medium | 20+ languages |

### Current UnaMentis Models

| Platform | Primary (on-device) | Primary (server) | Fallback |
|----------|-------------------|-----------------|----------|
| iOS | Kyutai Pocket TTS (100M) | Kyutai 1.6B | Apple AVSpeech |
| Android | Kyutai Pocket TTS (ONNX) | (planned) | Android TTS |

## Evaluation Output

```json
{
  "model": "chatterbox-0.1",
  "quality": {
    "mos_utmos": 4.3,
    "mos_wvmos": 3.9,
    "mos_average": 4.1,
    "intelligibility_wer": 0.027,
    "pronunciation_accuracy": 0.942,
    "pronunciation_details": {
      "total_terms": 200,
      "correct": 188,
      "incorrect": [
        {"term": "stoichiometry", "expected": "stɔɪ.ki.ˈɒm.ɪ.tri", "actual": "stoʊ.tʃi.ˈɒm.ɪ.tri"},
        {"term": "Euler", "expected": "ˈɔɪ.lər", "actual": "ˈjuː.lər"}
      ]
    },
    "prosody": {
      "pitch_range_hz": 145,
      "pitch_variation": 32.5,
      "speaking_rate_variation": 0.18,
      "prosody_score": 0.76
    }
  },
  "performance": {
    "ttfb_ms": 85,
    "rtf": 0.3,
    "model_size_mb": 800,
    "peak_memory_mb": 1200,
    "output_sample_rate": 24000
  },
  "samples": [
    {
      "text": "The Krebs cycle occurs in the mitochondrial matrix.",
      "audio_path": "samples/chatterbox/krebs_cycle.wav",
      "mos": 4.2,
      "pronunciation_correct": true
    }
  ]
}
```
