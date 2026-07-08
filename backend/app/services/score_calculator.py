from collections import namedtuple
from typing import List

_SKILLS_WEIGHT = 50
_EXPERIENCE_WEIGHT = 30
_QUALIFICATION_WEIGHT = 15
_SOFT_SKILLS_WEIGHT = 5

ScoreBreakdown = namedtuple("ScoreBreakdown", "skill experience qualification soft total")


def calculate_scores(
    matched_skills: List[str],
    required_skills: List[str],
    experience_match: bool,
    qualification_score: int,
    matched_keywords: List[str],
    jd_keywords: List[str],
) -> ScoreBreakdown:
    skill = round(len(matched_skills) / len(required_skills) * _SKILLS_WEIGHT) if required_skills else _SKILLS_WEIGHT
    experience = _EXPERIENCE_WEIGHT if experience_match else 0
    qualification = max(0, min(_QUALIFICATION_WEIGHT, qualification_score))
    soft = round(len(matched_keywords) / len(jd_keywords) * _SOFT_SKILLS_WEIGHT) if jd_keywords else _SOFT_SKILLS_WEIGHT

    total = max(0, min(100, skill + experience + qualification + soft))
    return ScoreBreakdown(skill, experience, qualification, soft, total)


def recommendation(score: int) -> str:
    if score >= 90:
        return "Excellent Match"
    if score >= 75:
        return "Strong Match"
    if score >= 60:
        return "Moderate Match"
    if score >= 40:
        return "Weak Match"
    return "Not Recommended"