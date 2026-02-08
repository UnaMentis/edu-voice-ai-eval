"""Seed built-in benchmark suites on first initialization."""


from .base import BaseStorage

BUILTIN_SUITES = [
    {
        "name": "Quick Scan",
        "slug": "quick_scan",
        "description": "Fast capability check (~5 min). MMLU subset, ARC Easy, GSM8K.",
        "model_type": "llm",
        "category": "education",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 5},
        "tasks": [
            {"name": "MMLU Elementary Math", "task_type": "mmlu", "education_tier": "elementary", "subject": "math", "config": {"lm_eval_tasks": ["mmlu_elementary_mathematics", "mmlu_formal_logic"]}},
            {"name": "ARC Easy", "task_type": "arc", "education_tier": "elementary", "subject": "science", "config": {"lm_eval_tasks": ["arc_easy"]}},
            {"name": "GSM8K", "task_type": "gsm8k", "education_tier": "elementary", "subject": "math", "config": {"lm_eval_tasks": ["gsm8k"]}},
            {"name": "MMLU HS Math", "task_type": "mmlu", "education_tier": "highschool", "subject": "math", "config": {"lm_eval_tasks": ["mmlu_high_school_mathematics"]}},
            {"name": "MMLU HS Biology", "task_type": "mmlu", "education_tier": "highschool", "subject": "biology", "config": {"lm_eval_tasks": ["mmlu_high_school_biology"]}},
        ],
    },
    {
        "name": "Education Focus",
        "slug": "education_focus",
        "description": "Comprehensive education assessment (~30 min). All four education tiers.",
        "model_type": "llm",
        "category": "education",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 30},
        "tasks": [
            # Tier 1: Elementary
            {"name": "MMLU Elementary", "task_type": "mmlu", "education_tier": "elementary", "subject": "general", "config": {"lm_eval_tasks": ["mmlu_elementary_mathematics", "mmlu_formal_logic"]}},
            {"name": "ARC Easy", "task_type": "arc", "education_tier": "elementary", "subject": "science", "config": {"lm_eval_tasks": ["arc_easy"]}},
            {"name": "GSM8K", "task_type": "gsm8k", "education_tier": "elementary", "subject": "math", "config": {"lm_eval_tasks": ["gsm8k"]}},
            # Tier 2: High School
            {"name": "MMLU HS Biology", "task_type": "mmlu", "education_tier": "highschool", "subject": "biology", "config": {"lm_eval_tasks": ["mmlu_high_school_biology"]}},
            {"name": "MMLU HS Chemistry", "task_type": "mmlu", "education_tier": "highschool", "subject": "chemistry", "config": {"lm_eval_tasks": ["mmlu_high_school_chemistry"]}},
            {"name": "MMLU HS Physics", "task_type": "mmlu", "education_tier": "highschool", "subject": "physics", "config": {"lm_eval_tasks": ["mmlu_high_school_physics"]}},
            {"name": "MMLU HS Math", "task_type": "mmlu", "education_tier": "highschool", "subject": "math", "config": {"lm_eval_tasks": ["mmlu_high_school_mathematics"]}},
            {"name": "MMLU HS History", "task_type": "mmlu", "education_tier": "highschool", "subject": "history", "config": {"lm_eval_tasks": ["mmlu_high_school_us_history", "mmlu_high_school_world_history"]}},
            {"name": "MMLU HS CS", "task_type": "mmlu", "education_tier": "highschool", "subject": "cs", "config": {"lm_eval_tasks": ["mmlu_high_school_computer_science"]}},
            {"name": "ARC Challenge", "task_type": "arc", "education_tier": "highschool", "subject": "science", "config": {"lm_eval_tasks": ["arc_challenge"]}},
            # Tier 3: Undergraduate
            {"name": "MMLU College", "task_type": "mmlu", "education_tier": "undergrad", "subject": "general", "config": {"lm_eval_tasks": ["mmlu_college_biology", "mmlu_college_chemistry", "mmlu_college_mathematics", "mmlu_college_physics", "mmlu_college_computer_science"]}},
            {"name": "MATH", "task_type": "math", "education_tier": "undergrad", "subject": "math", "config": {"lm_eval_tasks": ["math"]}},
            {"name": "MMLU-Pro", "task_type": "mmlu", "education_tier": "undergrad", "subject": "general", "config": {"lm_eval_tasks": ["mmlu_pro"]}},
            # Tier 4: Graduate
            {"name": "MMLU Professional", "task_type": "mmlu", "education_tier": "grad", "subject": "general", "config": {"lm_eval_tasks": ["mmlu_professional_medicine", "mmlu_professional_law", "mmlu_professional_accounting"]}},
            {"name": "GPQA", "task_type": "gpqa", "education_tier": "grad", "subject": "science", "config": {"lm_eval_tasks": ["gpqa"]}},
            # Non-tiered quality checks
            {"name": "TruthfulQA", "task_type": "truthfulqa", "config": {"lm_eval_tasks": ["truthfulqa_mc2"]}},
            {"name": "HellaSwag", "task_type": "hellaswag", "config": {"lm_eval_tasks": ["hellaswag"]}},
        ],
    },
    {
        "name": "Full LLM",
        "slug": "full_llm",
        "description": "Exhaustive LLM evaluation (~2 hours). All benchmarks including tutoring.",
        "model_type": "llm",
        "category": "education",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 120},
        "tasks": [],  # Inherits education_focus tasks + HumanEval, IFEval, TutorBench, OpenLearnLM
    },
    {
        "name": "STT Standard",
        "slug": "stt_standard",
        "description": "Standard STT accuracy across multiple datasets (~15 min).",
        "model_type": "stt",
        "category": "quality",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 15},
        "tasks": [
            {"name": "LibriSpeech Clean", "task_type": "wer", "config": {"dataset": "librispeech_clean"}},
            {"name": "LibriSpeech Other", "task_type": "wer", "config": {"dataset": "librispeech_other"}},
            {"name": "Common Voice EN", "task_type": "wer", "config": {"dataset": "common_voice_en"}},
            {"name": "TED-LIUM", "task_type": "wer", "config": {"dataset": "tedlium"}},
        ],
    },
    {
        "name": "STT Education",
        "slug": "stt_education",
        "description": "STT accuracy including educational domain vocabulary (~20 min).",
        "model_type": "stt",
        "category": "education",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 20},
        "tasks": [
            {"name": "LibriSpeech Clean", "task_type": "wer", "config": {"dataset": "librispeech_clean"}},
            {"name": "LibriSpeech Other", "task_type": "wer", "config": {"dataset": "librispeech_other"}},
            {"name": "Common Voice EN", "task_type": "wer", "config": {"dataset": "common_voice_en"}},
            {"name": "TED-LIUM", "task_type": "wer", "config": {"dataset": "tedlium"}},
            {"name": "Edu Vocabulary Tier 1", "task_type": "wer", "education_tier": "elementary", "config": {"dataset": "edu_tier1"}},
            {"name": "Edu Vocabulary Tier 2", "task_type": "wer", "education_tier": "highschool", "config": {"dataset": "edu_tier2"}},
            {"name": "Edu Vocabulary Tier 3", "task_type": "wer", "education_tier": "undergrad", "config": {"dataset": "edu_tier3"}},
            {"name": "Edu Vocabulary Tier 4", "task_type": "wer", "education_tier": "grad", "config": {"dataset": "edu_tier4"}},
        ],
    },
    {
        "name": "TTS Quality",
        "slug": "tts_quality",
        "description": "Comprehensive TTS quality assessment (~10 min). MOS, intelligibility, pronunciation.",
        "model_type": "tts",
        "category": "quality",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 10},
        "tasks": [
            {"name": "MOS Standard", "task_type": "mos", "config": {"sentences": "standard_100"}},
            {"name": "Intelligibility", "task_type": "intelligibility", "config": {"sentences": "standard_100"}},
            {"name": "Pronunciation - Science", "task_type": "pronunciation", "subject": "science", "config": {"term_set": "science_terms"}},
            {"name": "Pronunciation - Math", "task_type": "pronunciation", "subject": "math", "config": {"term_set": "math_terms"}},
            {"name": "Prosody", "task_type": "prosody", "config": {"sentences": "standard_100"}},
        ],
    },
    {
        "name": "On-Device",
        "slug": "on_device",
        "description": "On-device focused evaluation with performance metrics (~15 min).",
        "model_type": "llm",
        "category": "performance",
        "is_builtin": True,
        "config": {"estimated_duration_minutes": 15, "measure_performance": True},
        "tasks": [
            {"name": "MMLU Elementary", "task_type": "mmlu", "education_tier": "elementary", "config": {"lm_eval_tasks": ["mmlu_elementary_mathematics"]}},
            {"name": "ARC Easy", "task_type": "arc", "education_tier": "elementary", "config": {"lm_eval_tasks": ["arc_easy"]}},
            {"name": "GSM8K", "task_type": "gsm8k", "education_tier": "elementary", "config": {"lm_eval_tasks": ["gsm8k"]}},
        ],
    },
]


async def seed_builtin_suites(storage: BaseStorage) -> None:
    """Insert predefined benchmark suites if they don't exist."""
    for suite_data in BUILTIN_SUITES:
        existing = await storage.get_suite_by_slug(suite_data["slug"])
        if existing:
            continue

        # Copy to avoid mutating the global
        suite_dict = dict(suite_data)
        tasks = suite_dict.pop("tasks", [])
        suite_id = await storage.create_suite(suite_dict)

        for i, task in enumerate(tasks):
            task["suite_id"] = suite_id
            task["order_index"] = i
            if "config" not in task:
                task["config"] = {}
            await storage.create_task(task)
