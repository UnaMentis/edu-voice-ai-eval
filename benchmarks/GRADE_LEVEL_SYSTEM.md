# Grade-Level Education Capability System

The signature feature of this evaluation system: a four-tier education capability rating that tells you what grade level of content a model can handle reliably.

## Tier Definitions

| Tier | Grade Levels | Description | Target Audience |
|------|-------------|-------------|-----------------|
| **Tier 1: Elementary** | Grades 5-8 | Basic concepts, simple vocabulary, straightforward reasoning | Middle school students |
| **Tier 2: High School** | Grades 9-12 | Subject-specific knowledge, moderate reasoning, AP-level content | High school students |
| **Tier 3: Undergraduate** | College | College-level depth, complex reasoning, specialized terminology | University students |
| **Tier 4: Graduate** | Graduate/PhD | Professional expertise, cutting-edge knowledge, expert conversation | Graduate students, professionals |

## Benchmark Mapping

### Tier 1: Elementary (Grades 5-8)

| Benchmark ID | Upstream Task | Subject | Weight |
|-------------|--------------|---------|--------|
| `edu_tier1_mmlu_elementary` | mmlu_elementary_mathematics, mmlu_formal_logic | Math/Logic | 1.0 |
| `edu_tier1_arc_easy` | arc_easy | Science | 1.0 |
| `edu_tier1_gsm8k` | gsm8k | Math | 1.0 |

**What passing means:** The model can correctly answer basic math word problems, simple science questions, and elementary logic puzzles. Suitable for tutoring younger students on foundational concepts.

### Tier 2: High School (Grades 9-12)

| Benchmark ID | Upstream Task | Subject | Weight |
|-------------|--------------|---------|--------|
| `edu_tier2_mmlu_hs_bio` | mmlu_high_school_biology | Biology | 1.0 |
| `edu_tier2_mmlu_hs_chem` | mmlu_high_school_chemistry | Chemistry | 1.0 |
| `edu_tier2_mmlu_hs_phys` | mmlu_high_school_physics | Physics | 1.0 |
| `edu_tier2_mmlu_hs_math` | mmlu_high_school_mathematics | Math | 1.0 |
| `edu_tier2_mmlu_hs_hist` | mmlu_high_school_us_history, mmlu_high_school_world_history | History | 1.0 |
| `edu_tier2_mmlu_hs_cs` | mmlu_high_school_computer_science | CS | 1.0 |
| `edu_tier2_arc_challenge` | arc_challenge | Science reasoning | 1.0 |

**What passing means:** The model handles AP-level content across STEM and humanities. Can explain biological processes, solve chemistry problems, discuss historical events with depth.

### Tier 3: Undergraduate (College)

| Benchmark ID | Upstream Task | Subject | Weight |
|-------------|--------------|---------|--------|
| `edu_tier3_mmlu_college` | mmlu_college_biology, mmlu_college_chemistry, mmlu_college_mathematics, mmlu_college_physics, mmlu_college_computer_science | Multi | 1.0 |
| `edu_tier3_math` | math | Advanced math | 1.0 |
| `edu_tier3_mmlu_pro` | mmlu_pro | Deep reasoning | 1.0 |

**What passing means:** The model handles college-level coursework. Can work through competition-level math problems, explain college biology and physics concepts, and handle nuanced multi-step reasoning.

### Tier 4: Graduate (Graduate/PhD)

| Benchmark ID | Upstream Task | Subject | Weight |
|-------------|--------------|---------|--------|
| `edu_tier4_mmlu_professional` | mmlu_professional_medicine, mmlu_professional_law, mmlu_professional_accounting | Professional | 1.0 |
| `edu_tier4_gpqa` | gpqa | Expert Q&A | 1.5 |

**What passing means:** The model handles graduate and professional-level content. Can discuss specialized medical, legal, or engineering topics with expert-level accuracy.

## Scoring Algorithm

### Per-Tier Score Calculation

```python
def calculate_tier_score(task_results: list[TaskResult], tier: EducationTier) -> float:
    """Calculate weighted average score for an education tier.

    Args:
        task_results: Results for tasks in this tier
        tier: Which education tier

    Returns:
        Score between 0 and 100
    """
    total_weight = sum(t.weight for t in task_results)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(t.score * t.weight for t in task_results)
    return weighted_sum / total_weight
```

### Pass/Fail Determination

```python
def assess_tier(score: float, threshold: float = 70.0) -> bool:
    """Determine if a model passes an education tier.

    Default threshold: 70% (configurable per evaluation)
    """
    return score >= threshold
```

### Maximum Passing Tier

```python
def get_max_passing_tier(tier_scores: dict[EducationTier, float], threshold: float = 70.0) -> EducationTier | None:
    """Find the highest education tier where the model passes.

    Tiers are assessed in order: Elementary -> High School -> Undergraduate -> Graduate.
    A model must pass all lower tiers to "earn" a higher tier rating.

    Example:
        Tier 1: 85% (pass), Tier 2: 72% (pass), Tier 3: 48% (fail)
        -> Max passing tier: HIGH_SCHOOL (Tier 2)
    """
    tier_order = [
        EducationTier.ELEMENTARY,
        EducationTier.HIGH_SCHOOL,
        EducationTier.UNDERGRADUATE,
        EducationTier.GRADUATE,
    ]

    max_tier = None
    for tier in tier_order:
        score = tier_scores.get(tier, 0)
        if score >= threshold:
            max_tier = tier
        else:
            break  # Must pass all lower tiers

    return max_tier
```

### Overall Education Score

```python
def calculate_overall_education_score(tier_scores: dict) -> float:
    """Weighted average across all tiers with declining weights.

    Lower tiers weighted more heavily because foundational capability matters more.
    """
    weights = {
        EducationTier.ELEMENTARY: 1.0,
        EducationTier.HIGH_SCHOOL: 1.0,
        EducationTier.UNDERGRADUATE: 0.8,
        EducationTier.GRADUATE: 0.6,
    }

    total_weight = sum(weights.values())
    weighted_sum = sum(tier_scores.get(tier, 0) * w for tier, w in weights.items())
    return weighted_sum / total_weight
```

## Threshold Considerations

The default 70% threshold is chosen because:
- Below 70%, a model makes too many errors to be a reliable tutor
- Above 70%, the model demonstrates sufficient understanding to help students learn
- This aligns roughly with a "C" grade in most educational systems

However, the threshold is **configurable** because:
- For safety-critical subjects (medicine, law), a higher threshold (80-85%) may be warranted
- For creative subjects, a lower threshold may be acceptable
- Different institutions have different standards

## Limitations

1. **Benchmarks test knowledge, not teaching ability.** A model that scores 90% on MMLU biology knows biology facts but may not explain them well. TutorBench and OpenLearnLM partially address this.

2. **Grade-level mapping is approximate.** MMLU subjects don't perfectly map to grade levels. "High school biology" on MMLU may include some content typically taught at college level.

3. **English-centric.** Current benchmarks are primarily English. Multilingual evaluation requires additional test sets.

4. **Static knowledge.** Benchmarks test factual recall on fixed datasets. They don't measure a model's ability to adapt explanations to a struggling student.

## Future Extensions

- **TutorBench integration:** Rubric-based tutoring quality scores mapped to tiers
- **OpenLearnLM integration:** Bloom's taxonomy-based assessment
- **Conversational evaluation:** Multi-turn tutoring dialogue quality
- **Multilingual tiers:** Grade-level assessment in languages beyond English
- **Subject-specific deep dives:** Detailed per-subject capability maps
