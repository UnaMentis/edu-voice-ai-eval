# LLM Evaluation Benchmarks

Language model evaluation methodology, covering both standard academic benchmarks and education-specific assessments.

## Standard Benchmarks

All run through lm-evaluation-harness. These establish a model's general capability.

### Knowledge and Reasoning

| Benchmark | Tasks | Metric | What It Tests |
|-----------|-------|--------|---------------|
| **MMLU** | 57 subjects | Accuracy (5-shot) | Broad knowledge, elementary to professional |
| **MMLU-Pro** | 57 subjects, 10 options | Accuracy | Harder reasoning variant of MMLU |
| **ARC Easy** | ~2,600 questions | Accuracy | Basic science reasoning |
| **ARC Challenge** | ~1,170 questions | Accuracy (25-shot) | Complex science reasoning |
| **HellaSwag** | ~10,000 questions | Accuracy (10-shot) | Common sense reasoning |

### Mathematics

| Benchmark | Tasks | Metric | What It Tests |
|-----------|-------|--------|---------------|
| **GSM8K** | 1,319 problems | Accuracy (5-shot) | Grade school math word problems |
| **MATH** | 5,000 problems | Accuracy (4-shot) | Competition-level mathematics |

### Factuality and Safety

| Benchmark | Tasks | Metric | What It Tests |
|-----------|-------|--------|---------------|
| **TruthfulQA** | 817 questions | MC2 accuracy | Factual accuracy, hallucination resistance |
| **IFEval** | ~500 prompts | Prompt-level accuracy | Instruction following capability |

### Code

| Benchmark | Tasks | Metric | What It Tests |
|-----------|-------|--------|---------------|
| **HumanEval** | 164 problems | Pass@1 | Code generation (Python) |

### Expert-Level

| Benchmark | Tasks | Metric | What It Tests |
|-----------|-------|--------|---------------|
| **GPQA** | 448 questions | Accuracy (0-shot) | Graduate-level science (PhD-difficulty) |

## Education-Specific Benchmarks

### TutorBench

**Source:** https://arxiv.org/abs/2510.02663, https://huggingface.co/datasets/tutorbench/tutorbench
**Integration:** Custom lm-eval-harness task definitions + LLM-judge scoring

Tests three core tutoring skills:
1. **Adaptive Explanations:** Can the model adjust its explanation when a student doesn't understand?
2. **Actionable Feedback:** Does the model give specific, helpful feedback on student work?
3. **Hint Generation:** Can the model give hints that guide without giving away the answer?

**Evaluation method:** The model generates tutoring responses to scenarios, scored by an LLM judge (Claude or GPT-4) using rubrics from the TutorBench paper.

```yaml
# test_sets/llm/custom_tasks/tutorbench_adaptive.yaml
task: tutorbench_adaptive_explanation
dataset_path: tutorbench/tutorbench
output_type: generate_until
generation_kwargs:
  max_gen_toks: 512
  temperature: 0.0
metric_list:
  - metric: llm_judge
    judge_model: "claude-sonnet-4-5-20250929"
    rubric: "adaptive_explanation_rubric"
```

### OpenLearnLM Benchmark

**Source:** https://arxiv.org/abs/2601.13882
**Integration:** Subset adapted as custom lm-eval-harness tasks

124K+ items organized by Bloom's taxonomy level:
- **Knowledge:** Factual recall
- **Comprehension:** Understanding and paraphrasing
- **Application:** Applying knowledge to new situations
- **Analysis:** Breaking down complex information
- **Synthesis:** Creating new ideas from existing knowledge
- **Evaluation:** Making judgments about quality or value

We integrate a representative subset (approximately 5,000 items) covering all six Bloom levels across core subjects.

### MathTutorBench

**Source:** https://eth-lre.github.io/mathtutorbench
**Integration:** Custom task definitions

Seven pedagogical tasks specific to math tutoring:
1. Diagnosing student errors
2. Providing scaffolded hints
3. Generating practice problems
4. Explaining solution steps
5. Assessing student understanding
6. Adapting difficulty level
7. Connecting concepts across topics

## On-Device Evaluation Additions

For models targeting mobile deployment (1-3B parameters), additional metrics are captured alongside quality benchmarks:

| Metric | Tool | What It Measures |
|--------|------|-----------------|
| Tokens/second | Custom timing | Inference throughput |
| Time to first token (ms) | Custom timing | Response latency |
| Peak memory (MB) | psutil / system monitor | RAM usage |
| Model load time (s) | Custom timing | Startup cost |
| GPU layer utilization | llama.cpp stats | Hardware acceleration |

### On-Device Performance Targets

Based on UnaMentis requirements:

| Metric | Target | Rationale |
|--------|--------|-----------|
| Tokens/sec | >30 | Readable streaming speed |
| TTFT | <200ms | Conversational responsiveness |
| Peak memory | <3GB | Fits alongside other app processes |
| Model size | <3GB | Reasonable download + storage |

## Predefined Suites

### `quick_scan`
Purpose: Fast check of a new model's general capability.
Tasks: MMLU (10-subject subset), ARC Easy, GSM8K
Duration: ~5 minutes
Tiers covered: 1-2

### `education_focus`
Purpose: Comprehensive education capability assessment.
Tasks: All four tier benchmarks + TruthfulQA + HellaSwag
Duration: ~30 minutes
Tiers covered: 1-4

### `full_llm`
Purpose: Exhaustive evaluation including all standard and education benchmarks.
Tasks: All MMLU, ARC, GSM8K, MATH, TruthfulQA, HumanEval, IFEval, GPQA, TutorBench, OpenLearnLM
Duration: ~2 hours
Tiers covered: 1-4 + non-tiered

### `on_device`
Purpose: Quick quality + performance for on-device candidates.
Tasks: `quick_scan` benchmarks + performance metrics
Duration: ~15 minutes
Additional: tokens/sec, memory, model load time

## Key Models to Track

### On-Device Candidates (1-3B)

| Model | Params | Format | Notes |
|-------|--------|--------|-------|
| Qwen 2.5 1.5B Instruct | 1.5B | GGUF | Strong reasoning for size |
| Qwen 2.5 3B Instruct | 3B | GGUF | Current sweet spot |
| SmolLM2 1.7B | 1.7B | GGUF | Efficient architecture |
| Gemma 3 1B | 1B | GGUF | Google's small model |
| Llama 3.2 1B/3B | 1-3B | GGUF | Meta's mobile models |
| Phi-4 Mini | 3.8B | GGUF | Microsoft's small model |
| Ministral 3B | 3B | GGUF | Current UnaMentis choice |

### Server Candidates (7B+)

| Model | Params | Notes |
|-------|--------|-------|
| Qwen 2.5 7B/14B/32B/72B | 7-72B | Strong across sizes |
| Llama 3.3 70B | 70B | Meta's flagship |
| Mistral 7B/Mixtral | 7-47B | Efficient MoE |
| DeepSeek V3 | 671B MoE | Dense-equivalent ~37B |
| Phi-4 | 14B | Strong reasoning |

### Reference Models (quality ceiling)

| Model | Source | Role |
|-------|--------|------|
| Claude 3.5 Sonnet | Anthropic API | Primary reference |
| GPT-4o | OpenAI API | Secondary reference |

Reference models establish the quality ceiling. All other models are measured as a percentage of the reference score.
