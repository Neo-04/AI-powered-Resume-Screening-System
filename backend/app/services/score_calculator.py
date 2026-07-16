from collections import namedtuple

_SKILLS_WEIGHT = 50
_EXPERIENCE_WEIGHT = 30
_QUALIFICATION_WEIGHT = 15
_SOFT_SKILLS_WEIGHT = 5

ScoreBreakdown = namedtuple(
    "ScoreBreakdown", "skill experience qualification soft total"
)


def calculate_scores(
    skill_credit: float,
    required_skill_count: int,
    experience_match: bool,
    qualification_score: float,
    soft_credit: float,
    jd_keyword_count: int,
) -> ScoreBreakdown:
    skill = (
        round(skill_credit / required_skill_count * _SKILLS_WEIGHT)
        if required_skill_count
        else _SKILLS_WEIGHT
    )
    experience = _EXPERIENCE_WEIGHT if experience_match else 0
    soft = (
        round(soft_credit / jd_keyword_count * _SOFT_SKILLS_WEIGHT)
        if jd_keyword_count
        else _SOFT_SKILLS_WEIGHT
    )
    qualification = max(0, min(_QUALIFICATION_WEIGHT, round(qualification_score)))

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
