# Web Dashboard Design

Rich, interactive web dashboard built with Next.js 16 + React 19 + Tailwind CSS 4 + ECharts. Dark theme. Communicates with the FastAPI backend on port 8790.

## Navigation

Top-level nav with 7 sections:

```
[Overview] [Models] [Runs] [Results] [Compare] [Benchmarks] [Reports]
```

## Page 1: Overview Dashboard

The landing page. At-a-glance summary of evaluation activity.

```
+------------------------------------------------------------------+
| EVALUATION OVERVIEW                                   [+ New Run] |
+------------------------------------------------------------------+
|                                                                    |
| ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              |
| │ Models   │ │ Runs     │ │ Active   │ │ Avg      │              |
| │ 47       │ │ 231      │ │ 2        │ │ Score    │              |
| │registered│ │completed │ │ running  │ │ 78.4/100 │              |
| └──────────┘ └──────────┘ └──────────┘ └──────────┘              |
|                                                                    |
| RECENT RUNS                                                        |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Run       Model             Suite        Score  Status   When  │ |
| │ run-042   Qwen 2.5 7B      EduBench     82.3   Done     2h   │ |
| │ run-041   Whisper Lg V3     STT-EDU      91.7   Done     4h   │ |
| │ run-040   Llama 3.3 70B    Full-LLM     ----   Running  Now  │ |
| │ run-039   Ministral-3B     EduBench     65.1   Done     1d   │ |
| │ run-038   Chatterbox 0.1   TTS-Quality  78.5   Done     1d   │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| ┌──────────────────────────┐ ┌──────────────────────────────────┐ |
| │ QUALITY vs SIZE          │ │ MODEL FAMILY TRENDS              │ |
| │ (scatter chart)          │ │ (line chart)                     │ |
| │                          │ │                                  │ |
| │  Score                   │ │  Score                           │ |
| │  100 ┤                   │ │  100 ┤    ╱── Qwen 2.5          │ |
| │      │     ○ GPT-4       │ │      │   ╱                      │ |
| │   80 ┤  ○ Llama70B       │ │   80 ┤──╱── Llama 3.x          │ |
| │      │    ○ Qwen7B       │ │      │ ╱                        │ |
| │   60 ┤      ○ Qwen3B     │ │   60 ┤╱                         │ |
| │      │          ○ Phi3   │ │      │── Mistral                │ |
| │   40 ┤                   │ │   40 ┤                           │ |
| │      └────────────────   │ │      └──────────────────         │ |
| │       1B  3B  7B  70B    │ │       v1   v2   v3   v4         │ |
| │       Parameters         │ │       Version                    │ |
| └──────────────────────────┘ └──────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `OverviewPanel`, `StatCard` (x4), `RecentRunsTable`, `QualitySizeScatter`, `FamilyTrendChart`

## Page 2: Model Registry

Browse, search, and register models.

```
+------------------------------------------------------------------+
| MODEL REGISTRY                  [+ Import from HF] [+ Register]  |
+------------------------------------------------------------------+
|                                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Type: [All ▼]  Target: [All ▼]  Family: [All ▼]  [Search___] │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| [All (47)] [LLM (24)] [STT (8)] [TTS (10)] [VAD (3)] [Emb (2)]  |
|                                                                    |
| ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────┐ |
| │ ★ Qwen 2.5 7B       │ │ Whisper Large V3    │ │ Chatterbox   │ |
| │ LLM | Server | 7.6B │ │ STT | Server | 1.6B │ │ TTS | Server │ |
| │ GGUF Q4_K_M  4.2GB  │ │ FP16 | 3.1GB       │ │ 0.5B | 0.8GB│ |
| │ Ctx: 32K            │ │ WER: 4.2% (LBS)    │ │ MOS: 4.1    │ |
| │ Tiers: HS, UG       │ │ Langs: 100+        │ │ Langs: EN   │ |
| │                      │ │                     │ │              │ |
| │ [Evaluate] [Details] │ │ [Evaluate] [Details]│ │ [Eval] [Det]│ |
| └─────────────────────┘ └─────────────────────┘ └──────────────┘ |
| ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────┐ |
| │ Ministral 3B        │ │ Moonshine 240M      │ │ Kokoro 82M   │ |
| │ LLM | On-device     │ │ STT | On-device     │ │ TTS | On-dev │ |
| │ GGUF Q4_K_M  2.1GB  │ │ ONNX | 240MB       │ │ 82M | 100MB │ |
| │ ...                  │ │ ...                 │ │ ...          │ |
| └─────────────────────┘ └─────────────────────┘ └──────────────┘ |
+------------------------------------------------------------------+
```

**HuggingFace Import Modal:**
```
┌──────────────────────────────────────────┐
│ Import from HuggingFace                  │
│                                          │
│ Search: [whisper-large-v3___________]    │
│ Type: [STT ▼]  Target: [Server ▼]       │
│                                          │
│ Results:                                 │
│ ┌──────────────────────────────────────┐ │
│ │ openai/whisper-large-v3      [Add]  │ │
│ │ 1.6B params, safetensors, 100+ lang │ │
│ ├──────────────────────────────────────┤ │
│ │ openai/whisper-large-v3-turbo [Add] │ │
│ │ 0.8B params, faster variant         │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [Cancel]                                 │
└──────────────────────────────────────────┘
```

★ = Reference model (e.g., GPT-4 used as quality ceiling)

**Components:** `ModelRegistryPanel`, `ModelCard`, `ModelFilterBar`, `HuggingFaceImportModal`

## Page 3: Evaluation Runs

Queue management, active monitoring, and run history.

```
+------------------------------------------------------------------+
| EVALUATION RUNS                         [+ New Run] [Manage Queue]|
+------------------------------------------------------------------+
|                                                                    |
| ACTIVE (1)                                                         |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ run-040: Llama 3.3 70B on Full-LLM                           │ |
| │ ████████████████████░░░░░░░░░░ 62%                            │ |
| │ Current: MMLU-Biology | Task 8/13 | ETA: 14 min              │ |
| │ Started: 10:15 AM | Duration: 23 min                         │ |
| │                                                    [Cancel]   │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| QUEUE (2)                                                          |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ #1 [P:High]  Phi-3.5 Mini + EduBench       [Cancel] [↑ ↓]   │ |
| │ #2 [P:Med]   Whisper Sm + STT-EDU          [Cancel] [↑ ↓]   │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| COMPLETED                                                          |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ [Status: All ▼] [Model: All ▼] [Suite: All ▼] [Sort: New ▼] │ |
| ├────────────────────────────────────────────────────────────────┤ |
| │ Run       Model             Suite        Score  Duration  When │ |
| │ run-042   Qwen 2.5 7B      EduBench     82.3   23 min    2h  │ |
| │ run-041   Whisper Lg V3     STT-EDU      91.7   8 min     4h  │ |
| │ run-039   Ministral-3B     EduBench     65.1   18 min    1d  │ |
| │ run-038   Chatterbox 0.1   TTS-Quality  78.5   5 min     1d  │ |
| │                                                                │ |
| │ [< 1 2 3 ... 12 >]                                           │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `RunsPanel`, `ActiveRunCard` (with WebSocket progress), `QueueList`, `CompletedRunsTable`

## Page 4: Results Dashboard

The flagship page. Grade-level matrix, scatter plots, trends, and delta charts.

```
+------------------------------------------------------------------+
| RESULTS                                         [Export] [Share]  |
+------------------------------------------------------------------+
|                                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Models: [Select models ▼▼▼]  Suite: [Education Focus ▼]      │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| GRADE-LEVEL CAPABILITY MATRIX                                      |
| ┌────────────────────────────────────────────────────────────────┐ |
| │                  Elementary  High School  Undergrad  Graduate   │ |
| │ ★ Claude Ref     ██ 96      ██ 95        ██ 93      ██ 90    │ |
| │ Llama 3.3 70B    ██ 85      ██ 89        ██ 84      ██ 72    │ |
| │ Qwen 2.5 7B      ██ 78      ██ 82        ██ 71      ░░ 54   │ |
| │ Ministral 3B     ██ 72      ██ 68        ░░ 45      ░░ 22   │ |
| │ Qwen 2.5 3B      ██ 75      ██ 72        ░░ 48      ░░ 23   │ |
| │ Phi-3 Mini        ██ 62      ░░ 48        ░░ 31      ░░ 18   │ |
| │                                                                │ |
| │ ██ = Pass (>= 70%)   ░░ = Fail (< 70%)   Threshold: [70% ▼] │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| [Scatter] [Trends] [Delta] [Breakdown]                             |
|                                                                    |
| QUALITY vs PERFORMANCE (Scatter tab)                               |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Tokens/sec                                                     │ |
| │  300 ┤                                  ● Phi-3 Mini          │ |
| │      │                                                         │ |
| │  200 ┤                         ● Qwen 3B                      │ |
| │      │                   ● Ministral 3B                        │ |
| │  100 ┤            ● Qwen 7B                                   │ |
| │      │                                                         │ |
| │   30 ┤ ● Llama 70B                                            │ |
| │      └─────────────────────────────────────                    │ |
| │        40    50    60    70    80    90   Score                 │ |
| │                                                                │ |
| │ Bubble size = parameter count                                  │ |
| │ ───── Pareto frontier (quality/speed tradeoff)                │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| DELTA FROM REFERENCE (Delta tab)                                   |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Reference: Claude 3.5 Sonnet (100%)                            │ |
| │                                                                │ |
| │ Llama 3.3 70B  |████████████████████████████████████ | 89%    │ |
| │ Qwen 2.5 7B    |█████████████████████████████████   | 82%    │ |
| │ Qwen 2.5 3B    |████████████████████████████        | 72%    │ |
| │ Ministral 3B   |████████████████████████            | 65%    │ |
| │ Phi-3 Mini      |██████████████████                  | 52%    │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `ResultsPanel`, `GradeLevelMatrix` (ECharts heatmap), `QualityPerformanceScatter`, `FamilyTrendChart`, `DeltaFromReferenceChart`, `BenchmarkBreakdownTable`

## Page 5: Model Comparison

Interactive side-by-side comparison of 2-5 models.

```
+------------------------------------------------------------------+
| MODEL COMPARISON                                                   |
+------------------------------------------------------------------+
|                                                                    |
| Select models (2-5):                                               |
| [Qwen 2.5 7B ▼] [Llama 3.3 70B ▼] [Ministral 3B ▼] [+ Add]    |
|                                                                    |
| OVERVIEW                                                           |
| ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   |
| │ Qwen 2.5 7B      │ │ Llama 3.3 70B    │ │ Ministral 3B     │   |
| │ Score: 82.3       │ │ Score: 89.1       │ │ Score: 65.1      │   |
| │ 7.6B params       │ │ 70B params        │ │ 3B params        │   |
| │ 4.2 GB            │ │ 39 GB             │ │ 2.1 GB           │   |
| │ Server             │ │ Server            │ │ On-device        │   |
| │ Max: Undergrad     │ │ Max: Graduate     │ │ Max: HS          │   |
| └──────────────────┘ └──────────────────┘ └──────────────────┘   |
|                                                                    |
| RADAR CHART                                                        |
| ┌────────────────────────────────────────────────────────────────┐ |
| │                    Math                                        │ |
| │                     /\                                         │ |
| │                    /  \                                        │ |
| │         Science  /    \  Tutoring                              │ |
| │                 / ╱──╲ \                                       │ |
| │                ╱╱    ╲╲                                        │ |
| │     Reasoning ╱  ╱──╲  ╲ Speed                                │ |
| │               ╲  ╲──╱  ╱                                      │ |
| │                ╲╲    ╱╱                                        │ |
| │                 \ ╲──╱ /                                       │ |
| │         Safety   \    /  Factuality                            │ |
| │                    \  /                                        │ |
| │                     \/                                         │ |
| │              Efficiency                                        │ |
| │                                                                │ |
| │ ── Qwen 2.5  ── Llama 3.3  ── Ministral 3B                  │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| DETAILED TASK BREAKDOWN                                            |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Task              Qwen 2.5  Llama 3.3  Ministral  Best       │ |
| │ MMLU Biology      78.4      85.2       62.1       Llama ▲    │ |
| │ MMLU Physics      81.2      87.8       65.3       Llama ▲    │ |
| │ ARC Challenge     71.5      82.3       68.9       Llama ▲    │ |
| │ GSM8K             82.3      84.1       78.1       Llama ▲    │ |
| │ TruthfulQA        65.2      71.3       71.3       Tie        │ |
| │ Tokens/sec        145       32         280        Minist ▲   │ |
| │ Memory (GB)       5.8       42.3       2.8        Minist ▲   │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| Delta highlighting: green = best in row, red = worst in row        |
+------------------------------------------------------------------+
```

**Components:** `ComparisonPanel`, `ComparisonBuilder`, `ModelSummaryCard`, `RadarChart`, `ComparisonTable`

## Page 6: STT Detail View

Shown when viewing results for an STT model.

```
+------------------------------------------------------------------+
| STT EVALUATION: Whisper Large V3                                   |
+------------------------------------------------------------------+
|                                                                    |
| ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              |
| │ Overall  │ │ Edu-     │ │ RTFx     │ │ Size     │              |
| │ WER      │ │ Domain   │ │          │ │          │              |
| │ 4.2%     │ │ WER 5.8% │ │ 0.3x     │ │ 3.1 GB   │              |
| └──────────┘ └──────────┘ └──────────┘ └──────────┘              |
|                                                                    |
| WER BY DATASET (horizontal bar chart)                              |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ LibriSpeech Clean  |██                          | 2.1%        │ |
| │ LibriSpeech Other  |████                        | 4.8%        │ |
| │ Common Voice EN    |█████                       | 5.2%        │ |
| │ TED-LIUM           |████                        | 4.5%        │ |
| │ Edu Vocabulary      |███████                     | 7.3%        │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| DOMAIN-SPECIFIC WER (heatmap)                                      |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Biology  Physics  Math   CS     History  Chemistry  Literature │ |
| │  6.8%    5.1%     8.2%   3.2%   4.5%    7.9%       4.1%      │ |
| │  ████    ███      █████  ██     ███     █████       ███       │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| ON-DEVICE FEASIBILITY                                              |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Model Size:   3.1 GB (exceeds 1 GB on-device target)          │ |
| │ RTFx:         0.3x (below 1.0x real-time threshold)           │ |
| │ Memory Peak:  4.2 GB                                          │ |
| │                                                                │ |
| │ Verdict: SERVER ONLY                                           │ |
| │ Consider: Whisper Small (244 MB) or Moonshine (240 MB)        │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `STTDetailPanel`, `WERBarChart`, `DomainWERHeatmap`, `FeasibilityCard`

## Page 7: TTS Detail View

Shown when viewing results for a TTS model.

```
+------------------------------------------------------------------+
| TTS EVALUATION: Chatterbox 0.1                                     |
+------------------------------------------------------------------+
|                                                                    |
| ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              |
| │ MOS      │ │ Pronunc. │ │ Prosody  │ │ Intell.  │              |
| │ 4.1/5.0  │ │ 94.2%    │ │ 3.8/5.0  │ │ 97.3%    │              |
| └──────────┘ └──────────┘ └──────────┘ └──────────┘              |
|                                                                    |
| MOS SCORES (grouped bar chart)                                     |
| ┌────────────────────────────────────────────────────────────────┐ |
| │           UTMOS    WVMOS    Average                            │ |
| │ Chatter   ████4.3  ████3.9  ████4.1                           │ |
| │ Piper     ███ 3.2  ███ 3.1  ███ 3.2                           │ |
| │ Kokoro    ████3.8  ████3.7  ████3.8                           │ |
| │ ElevenL   █████4.5 █████4.4 █████4.5                          │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| PRONUNCIATION ACCURACY                                             |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ 188/200 terms correct (94.2%)                                  │ |
| │                                                                │ |
| │ CORRECT:                                                       │ |
| │ mitochondria ✓  |  Pythagorean ✓  |  epigenetics ✓            │ |
| │ Schrodinger ✓   |  eigenvalue ✓   |  Lagrangian ✓             │ |
| │                                                                │ |
| │ INCORRECT:                                                     │ |
| │ stoichiometry ✗  (stoy-chee-OM vs stoy-kee-OM)               │ |
| │ Euler ✗          (YOO-ler vs OY-ler)                          │ |
| │ Bernoulli ✗      (ber-NOO-lee vs ber-NUH-lee)                │ |
| │ ...8 more                                                      │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| AUDIO SAMPLES                                                      |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ "The Krebs cycle is a series of chemical reactions..."         │ |
| │ [▶ Play Chatterbox]  [▶ Play Piper]  [▶ Play ElevenLabs]     │ |
| │                                                                │ |
| │ "Euler's identity connects five fundamental constants..."      │ |
| │ [▶ Play Chatterbox]  [▶ Play Piper]  [▶ Play ElevenLabs]     │ |
| │                                                                │ |
| │ "The Pythagorean theorem states that in a right triangle..."   │ |
| │ [▶ Play Chatterbox]  [▶ Play Piper]  [▶ Play ElevenLabs]     │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| INTELLIGIBILITY PIPELINE                                           |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Text ──► TTS ──► Audio ──► STT ──► Transcript ──► Compare    │ |
| │                                                                │ |
| │ Round-trip WER: 2.7%                                          │ |
| │ STT used: Whisper Large V3                                    │ |
| │ Test sentences: 100                                            │ |
| │ Perfect transcriptions: 94/100                                 │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `TTSDetailPanel`, `MOSComparisonChart`, `PronunciationAccuracyTable`, `AudioSamplePlayer`, `IntelligibilityPipeline`

## Page 8: Benchmark Suites

Manage built-in and custom benchmark suites.

```
+------------------------------------------------------------------+
| BENCHMARK SUITES                              [+ Create Suite]    |
+------------------------------------------------------------------+
|                                                                    |
| [All] [LLM (4)] [STT (2)] [TTS (2)]                              |
|                                                                    |
| BUILT-IN                                                           |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Education Focus (LLM)                            [Configure]   │ |
| │ Grade-level MMLU + TutorBench + educational reasoning          │ |
| │ Tasks: 12 | Tiers: All 4 | Est: 30 min | Last run: 2h ago    │ |
| ├────────────────────────────────────────────────────────────────┤ |
| │ Quick Scan (LLM)                                 [Configure]   │ |
| │ MMLU subset + ARC Easy + GSM8K                                │ |
| │ Tasks: 3 | Tiers: 1-2 | Est: 5 min                           │ |
| ├────────────────────────────────────────────────────────────────┤ |
| │ STT Education (STT)                              [Configure]   │ |
| │ WER on standard + educational domain vocabulary                │ |
| │ Datasets: 5 | Domain terms: 800 | Est: 15 min                │ |
| ├────────────────────────────────────────────────────────────────┤ |
| │ TTS Quality (TTS)                                [Configure]   │ |
| │ MOS + pronunciation + intelligibility + prosody                │ |
| │ Test sentences: 200 | Est: 10 min                             │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| CUSTOM                                                             |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ (empty state)                                                  │ |
| │ Create custom suites by combining benchmarks and test sets.    │ |
| │ [+ Create Custom Suite]                                        │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

## Page 9: Reports and Sharing

Export, import, and share results.

```
+------------------------------------------------------------------+
| REPORTS & SHARING                                                  |
+------------------------------------------------------------------+
|                                                                    |
| GENERATE REPORT                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Run: [Select run ▼]                                           │ |
| │ Format: [PDF ▼]                                               │ |
| │ Include: [✓] Summary  [✓] Charts  [✓] Tasks  [✓] Recommend. │ |
| │ [Generate Report]                                              │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| EXPORT / IMPORT                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ [Export All as VLEF]  [Export as CSV]  [Import VLEF File]      │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| SHARED LINKS                                                       |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ Link            Type         Views   Expires   Actions         │ |
| │ /share/abc123   Run Report   42      Never     [Copy] [Delete]│ |
| │ /share/def456   Comparison   12      7 days    [Copy] [Delete]│ |
| │                                                                │ |
| │ [+ Create Share Link]                                          │ |
| └────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------+
```

**Components:** `ReportsPanel`, `ReportGenerator`, `ExportImportBar`, `SharedLinksTable`

## Chart Library

All charts use [ECharts](https://echarts.apache.org/) via a shared `EChartsWrapper` component. Chart types used:

| Chart | ECharts Type | Used In |
|-------|-------------|---------|
| Grade-Level Matrix | Heatmap | Results page |
| Quality vs Size Scatter | Scatter | Overview, Results |
| Model Family Trends | Line | Overview, Results |
| Delta from Reference | Bar (horizontal) | Results |
| WER by Dataset | Bar (horizontal) | STT Detail |
| Domain WER Heatmap | Heatmap | STT Detail |
| MOS Comparison | Bar (grouped) | TTS Detail |
| Radar Chart | Radar | Comparison |
| Progress Bar | Custom | Runs page |

## Responsive Design

- Desktop-first (evaluation is a desktop workflow)
- Grid layouts collapse to single column below 1024px
- Charts resize responsively
- Tables switch to card view on narrow screens

## Theme

- Dark background (slate-900/950)
- Accent colors by model type: blue (LLM), green (STT), purple (TTS), orange (VAD)
- Pass/fail: green-500 / red-500
- Score intensity: gradient from red (low) through yellow to green (high)
