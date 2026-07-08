from backend.app.schemas.matching import MatchResult
from backend.app.services import (
    experience_matcher,
    jd_parser,
    qualification_matcher,
    resume_parser,
    score_calculator,
    skill_matcher,
    soft_skill_matcher,
)


def _parsed_resume(resume_id: str):
    return resume_parser.structured_resume_store.get(resume_id) or resume_parser.parse_resume(resume_id)


def _parsed_jd(jd_id: str):
    return jd_parser.structured_jd_store.get(jd_id) or jd_parser.parse_jd(jd_id)


def run_match(resume_id: str, jd_id: str) -> MatchResult:
    resume = _parsed_resume(resume_id)
    jd = _parsed_jd(jd_id)

    matched_skills, missing_skills, additional_skills = skill_matcher.match_skills(
        resume.skills, jd.required_skills
    )
    qualification_match, matching_reason = qualification_matcher.match_qualification(
        resume.degree, resume.branch, jd.preferred_qualification
    )
    experience_match = experience_matcher.match_experience(resume.experience_years, jd.experience)

    resume_text = " ".join(resume.achievements + resume.experience + resume.projects)
    matched_keywords = soft_skill_matcher.match_soft_skills(jd.keywords, resume_text)

    qualification_points = qualification_matcher.qualification_score(
        resume.degree, resume.branch, jd.preferred_qualification
    )
    scores = score_calculator.calculate_scores(
        matched_skills, jd.required_skills, experience_match, qualification_points,
        matched_keywords, jd.keywords,
    )

    return MatchResult(
        match_score=scores.total,
        skill_score=scores.skill,
        experience_score=scores.experience,
        qualification_score=scores.qualification,
        soft_skill_score=scores.soft,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        additional_skills=additional_skills,
        qualification_match=qualification_match,
        matching_reason=matching_reason,
        experience_match=experience_match,
        matched_keywords=matched_keywords,
        recommendation=score_calculator.recommendation(scores.total),
    )