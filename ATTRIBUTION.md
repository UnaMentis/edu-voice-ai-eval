# Attribution

This project builds on the exceptional work of the open-source AI community. We integrate, wrap, and orchestrate these projects, and we are deeply grateful to their creators and contributors.

## Core Evaluation Engines

### EleutherAI lm-evaluation-harness
- **Repository:** https://github.com/EleutherAI/lm-evaluation-harness
- **License:** MIT
- **Role:** Core LLM benchmarking engine. The de facto standard for LLM evaluation, powering HuggingFace's Open LLM Leaderboard. We wrap this as our primary LLM evaluation plugin.
- **Citation:** Gao et al., "A framework for few-shot language model evaluation" (2024)

### HuggingFace Open ASR Leaderboard
- **Repository:** https://github.com/huggingface/open_asr_leaderboard
- **Leaderboard:** https://huggingface.co/spaces/hf-audio/open_asr_leaderboard
- **License:** Apache 2.0
- **Role:** STT evaluation framework. Provides the methodology and evaluation scripts for benchmarking speech recognition models across 11 datasets.

### Picovoice Speech-to-Text Benchmark
- **Repository:** https://github.com/Picovoice/speech-to-text-benchmark
- **License:** Apache 2.0
- **Role:** Complementary STT evaluation with Core-Hour efficiency metrics, Word Emission Latency, and model size tracking. Particularly valuable for on-device feasibility assessment.

## Quality Scoring

### UTMOS (UTokyo-SaruLab MOS Prediction)
- **Repository:** https://github.com/sarulab-speech/UTMOS22
- **License:** MIT
- **Role:** Automated Mean Opinion Score prediction for TTS quality assessment. Predicts human quality ratings from audio features.
- **Citation:** Saeki et al., "UTMOS: UTokyo-SaruLab System for VoiceMOS Challenge 2022" (2022)

### WVMOS (Wav2Vec MOS)
- **Repository:** https://github.com/AndreevP/wvmos
- **License:** MIT
- **Role:** Complementary automated MOS predictor. We average UTMOS and WVMOS scores for more robust quality assessment.

## Education-Specific Benchmarks

### OpenLearnLM Benchmark
- **Paper:** https://arxiv.org/abs/2601.13882
- **Published:** January 2026
- **Role:** The most comprehensive education-specific LLM benchmark. 124K+ items evaluating Knowledge, Skills, and Attitude using Bloom's taxonomy. We integrate a subset as custom evaluation tasks.

### TutorBench
- **Paper:** https://arxiv.org/abs/2510.02663
- **Dataset:** https://huggingface.co/datasets/tutorbench/tutorbench
- **Published:** October 2025
- **Role:** Expert-curated tutoring quality assessment. 1,490 samples testing adaptive explanations, actionable feedback, and hint generation at high school and AP-level STEM.

### MathTutorBench
- **Website:** https://eth-lre.github.io/mathtutorbench
- **Published:** 2025
- **Role:** Mathematical tutoring capability evaluation across 7 concrete pedagogical tasks.

## Standard Benchmarks

We use these well-established benchmarks through lm-evaluation-harness:

| Benchmark | Authors/Source | Role |
|-----------|---------------|------|
| MMLU | Hendrycks et al. (2021) | 57-subject knowledge assessment spanning elementary to professional |
| MMLU-Pro | Wang et al. (2024) | Harder reasoning-focused variant with 10-option questions |
| ARC | Clark et al. (2018) | AI2 Reasoning Challenge for science question answering |
| TruthfulQA | Lin et al. (2022) | Factual accuracy and hallucination resistance |
| GSM8K | Cobbe et al. (2021) | Grade school math word problems |
| MATH | Hendrycks et al. (2021) | Competition-level mathematics |
| HumanEval | Chen et al. (2021) | Code generation and problem solving |
| IFEval | Zhou et al. (2023) | Instruction following capability |
| GPQA | Rein et al. (2023) | Graduate-level Google-Proof Q&A |
| HellaSwag | Zellers et al. (2019) | Common sense and sentence completion |

## STT Evaluation Datasets

| Dataset | Source | Domain |
|---------|--------|--------|
| LibriSpeech | Panayotov et al. (2015) | Audiobook narration |
| Common Voice | Mozilla Foundation | Crowdsourced, diverse accents |
| VoxPopuli | Wang et al. (2021) | European Parliament |
| TED-LIUM | Rousseau et al. (2012) | TED talks (educational speech) |
| GigaSpeech | Chen et al. (2021) | Multi-domain (podcast, YouTube) |
| SPGISpeech | O'Neill et al. (2021) | Financial earnings calls |
| AMI | Carletta et al. (2005) | Meeting recordings |

## Tools and Libraries

| Tool | Repository | Role |
|------|-----------|------|
| pluggy | https://github.com/pytest-dev/pluggy | Plugin architecture framework |
| FastAPI | https://github.com/tiangolo/fastapi | Backend API framework |
| Click | https://github.com/pallets/click | CLI framework |
| jiwer | https://github.com/jitsi/jiwer | WER computation for STT evaluation |
| Montreal Forced Aligner | https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner | Pronunciation accuracy analysis |
| ECharts | https://github.com/apache/echarts | Dashboard charting library |

## On-Device Evaluation Tools

| Tool | Source | Role |
|------|--------|------|
| MobileAIBench | https://arxiv.org/abs/2406.10290 | Mobile LLM evaluation framework |
| ELIB | https://arxiv.org/abs/2508.11269 | Edge LLM Inference Benchmark |
| ollamabench | https://pypi.org/project/ollamabench | Local model performance benchmarking |

---

If we have inadvertently omitted any attribution, please open an issue and we will correct it immediately. Proper credit for the community's work is a core value of this project.
