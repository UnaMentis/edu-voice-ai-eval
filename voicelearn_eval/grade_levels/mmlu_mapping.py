"""Mapping of benchmark IDs to education tiers and lm-eval task names."""

from voicelearn_eval.core.models import EducationTier

# Maps our benchmark task education_tier values to EducationTier enum
TIER_FROM_STRING = {
    "elementary": EducationTier.ELEMENTARY,
    "highschool": EducationTier.HIGH_SCHOOL,
    "undergrad": EducationTier.UNDERGRADUATE,
    "grad": EducationTier.GRADUATE,
}

# Maps our benchmark IDs to lm-evaluation-harness task names
BENCHMARK_TO_LM_EVAL = {
    # Tier 1: Elementary
    "mmlu_elementary_mathematics": ["mmlu_elementary_mathematics"],
    "mmlu_formal_logic": ["mmlu_formal_logic"],
    "arc_easy": ["arc_easy"],
    "gsm8k": ["gsm8k"],
    # Tier 2: High School
    "mmlu_high_school_biology": ["mmlu_high_school_biology"],
    "mmlu_high_school_chemistry": ["mmlu_high_school_chemistry"],
    "mmlu_high_school_physics": ["mmlu_high_school_physics"],
    "mmlu_high_school_mathematics": ["mmlu_high_school_mathematics"],
    "mmlu_high_school_us_history": ["mmlu_high_school_us_history"],
    "mmlu_high_school_world_history": ["mmlu_high_school_world_history"],
    "mmlu_high_school_computer_science": ["mmlu_high_school_computer_science"],
    "arc_challenge": ["arc_challenge"],
    # Tier 3: Undergraduate
    "mmlu_college_biology": ["mmlu_college_biology"],
    "mmlu_college_chemistry": ["mmlu_college_chemistry"],
    "mmlu_college_mathematics": ["mmlu_college_mathematics"],
    "mmlu_college_physics": ["mmlu_college_physics"],
    "mmlu_college_computer_science": ["mmlu_college_computer_science"],
    "math": ["math"],
    "mmlu_pro": ["mmlu_pro"],
    # Tier 4: Graduate
    "mmlu_professional_medicine": ["mmlu_professional_medicine"],
    "mmlu_professional_law": ["mmlu_professional_law"],
    "mmlu_professional_accounting": ["mmlu_professional_accounting"],
    "gpqa": ["gpqa"],
    # Standard (non-tiered)
    "truthfulqa_mc2": ["truthfulqa_mc2"],
    "hellaswag": ["hellaswag"],
    "humaneval": ["humaneval"],
    "ifeval": ["ifeval"],
}

# Subjects for each lm-eval task
TASK_SUBJECTS = {
    "mmlu_elementary_mathematics": "math",
    "mmlu_formal_logic": "math",
    "arc_easy": "science",
    "gsm8k": "math",
    "mmlu_high_school_biology": "biology",
    "mmlu_high_school_chemistry": "chemistry",
    "mmlu_high_school_physics": "physics",
    "mmlu_high_school_mathematics": "math",
    "mmlu_high_school_us_history": "history",
    "mmlu_high_school_world_history": "history",
    "mmlu_high_school_computer_science": "cs",
    "arc_challenge": "science",
    "mmlu_college_biology": "biology",
    "mmlu_college_chemistry": "chemistry",
    "mmlu_college_mathematics": "math",
    "mmlu_college_physics": "physics",
    "mmlu_college_computer_science": "cs",
    "math": "math",
    "mmlu_pro": "general",
    "mmlu_professional_medicine": "medicine",
    "mmlu_professional_law": "law",
    "mmlu_professional_accounting": "accounting",
    "gpqa": "science",
    "truthfulqa_mc2": "factuality",
    "hellaswag": "reasoning",
    "humaneval": "code",
    "ifeval": "instruction_following",
}
