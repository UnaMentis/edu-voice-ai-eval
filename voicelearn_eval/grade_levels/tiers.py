"""Education tier definitions and constants."""

from voicelearn_eval.core.models import EducationTier

TIER_ORDER = [
    EducationTier.ELEMENTARY,
    EducationTier.HIGH_SCHOOL,
    EducationTier.UNDERGRADUATE,
    EducationTier.GRADUATE,
]

TIER_LABELS = {
    EducationTier.ELEMENTARY: "Elementary (Gr 5-8)",
    EducationTier.HIGH_SCHOOL: "High School (Gr 9-12)",
    EducationTier.UNDERGRADUATE: "Undergraduate",
    EducationTier.GRADUATE: "Graduate",
}

TIER_WEIGHTS = {
    EducationTier.ELEMENTARY: 1.0,
    EducationTier.HIGH_SCHOOL: 1.0,
    EducationTier.UNDERGRADUATE: 0.8,
    EducationTier.GRADUATE: 0.6,
}

DEFAULT_THRESHOLD = 70.0
