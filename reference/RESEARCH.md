# Research Reference

This architecture is informed by comprehensive research into AI model evaluation tools, education-specific benchmarks, and voice AI quality assessment methodologies.

## Primary Research Document

**Location:** `docs/explorations/voicelearn-model-evaluation-research.md` (in the UnaMentis repository)

This document, prepared February 2026, covers three evaluation domains:

1. **LLM Evaluation** - Survey of lm-evaluation-harness, education-specific benchmarks (OpenLearnLM, TutorBench, MathTutorBench), and the grade-level rating system concept
2. **STT Evaluation** - Survey of Open ASR Leaderboard, Picovoice STT Benchmark, and custom domain testing methodology
3. **TTS Evaluation** - Survey of UTMOS, WVMOS, pronunciation testing, and prosody analysis

The research document includes:
- Detailed tool descriptions with GitHub links and installation instructions
- Code examples for running each evaluation framework
- A four-phase implementation roadmap
- Current top models to track per category
- Key resources and citations

## How This Architecture Builds on the Research

| Research Recommendation | Architecture Decision |
|------------------------|----------------------|
| EleutherAI lm-evaluation-harness as core LLM engine | LLM plugin wraps lm-eval-harness (Python API + subprocess) |
| HuggingFace Open ASR + Picovoice for STT | STT plugin implements Open ASR methodology with Picovoice metrics |
| UTMOS/WVMOS for TTS quality | TTS plugin averages UTMOS and WVMOS scores |
| MMLU-based grade-level tiers | Grade-level system with 4 tiers, configurable thresholds |
| CI/CD pipeline with GitHub Actions | Workflows for scheduled, on-demand, and new-model-triggered evaluation |
| Results dashboard | 9-page Next.js web dashboard with grade-level matrix as signature view |
| Custom educational test sets | Domain vocabulary JSON format with tiered organization |

## Additional References

### Evaluation Frameworks
- [LLM Evaluation Resources Compendium](https://alopatenko.github.io/LLMEvaluation/) - Comprehensive list of LLM evaluation tools and benchmarks
- [Holistic Evaluation of Language Models (HELM)](https://crfm.stanford.edu/helm/) - Stanford's multi-metric LLM evaluation framework

### Education-Specific AI
- [AI in Education: A Comprehensive Survey](https://arxiv.org/abs/2305.06147) - Survey of AI applications in education
- [Bloom's Taxonomy and AI Assessment](https://arxiv.org/abs/2601.13882) - OpenLearnLM's use of Bloom's taxonomy for LLM evaluation

### On-Device AI
- [MLC-LLM](https://mlc.ai/mlc-llm/) - Mobile deployment framework for LLMs
- [MLX](https://ml-explore.github.io/mlx/) - Apple Silicon optimized ML framework
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Core local inference engine

### Voice AI Quality
- [VoiceMOS Challenge](https://voicemos-challenge-2022.github.io/) - Competition that produced UTMOS
- [StructTTSEval](https://arxiv.org/abs/2506.16381) - Expressiveness benchmark for TTS

## Context: UnaMentis Model Inventory

The evaluation system is designed with these current models in mind:

**On-Device:**
- LLM: Ministral-3B (GGUF Q4_K_M, 2.15GB)
- TTS: Kyutai Pocket TTS (100M params, Rust/Candle on iOS, ONNX on Android)
- VAD: Silero VAD (CoreML on iOS, TFLite on Android)
- STT: Apple Speech / GLM-ASR-Nano (iOS), planned (Android)

**Server-Side:**
- LLM: Claude 3.5 Sonnet (reference), GPT-4o, Ollama (Mistral 7B, Qwen 2.5:32B)
- TTS: Kyutai 1.6B, Fish Speech, Chatterbox, VibeVoice, Piper
- STT: Deepgram Nova-3, AssemblyAI, Groq Whisper, OpenAI Whisper, whisper.cpp, faster-whisper
- Embeddings: OpenAI text-embedding-3-small

The "on-device trajectory" is a key motivation: as smaller models improve, the day approaches when all three core capabilities (LLM, STT, TTS) run on-device at graduate-level quality. This evaluation system will track that progress quantitatively.
