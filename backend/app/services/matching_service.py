import logging
from typing import List, Tuple

from backend.app.schemas.matching import MatchResult
from backend.app.services import (
    experience_matcher,
    jd_parser,
    jd_service,
    qualification_matcher,
    resume_parser,
    score_calculator,
    semantic_matcher,
    skill_matcher,
    soft_skill_matcher,
)
from backend.app.utils import semantic_config

logger = logging.getLogger(__name__)


def _parsed_resume(resume_id: str):
    return resume_parser.structured_resume_store.get(resume_id) or resume_parser.parse_resume(resume_id)


def _parsed_jd(jd_id: str):
    return jd_parser.structured_jd_store.get(jd_id) or jd_parser.parse_jd(jd_id)


def _jd_text(jd_id: str) -> str:
    # raw text carries cues ("preferred", "relevant field") that parsing drops
    try:
        return jd_service.get_job_description(jd_id).text
    except Exception:
        return ""


def _consume_pairs(
    pairs: List[Tuple[str, str]],
    matched_skills: List[str],
    missing_skills: List[str],
    additional_skills: List[str],
) -> int:
    """Settle accepted pairs across all three lists; both sides are consumed."""
    accepted = 0
    for jd_skill, resume_skill in pairs:
        if jd_skill not in missing_skills or resume_skill not in additional_skills:
            continue
        missing_skills.remove(jd_skill)
        additional_skills.remove(resume_skill)
        matched_skills.append(jd_skill)
        accepted += 1
    return accepted


def run_match(resume_id: str, jd_id: str) -> MatchResult:
    resume = _parsed_resume(resume_id)
    jd = _parsed_jd(jd_id)

    matched_skills, missing_skills, additional_skills = skill_matcher.match_skills(
        resume.skills, jd.required_skills
    )
    matched_skills = list(matched_skills)
    missing_skills = list(missing_skills)
    additional_skills = list(additional_skills)
    exact_skill_units = len(matched_skills)

    # rule-based related pass; runs with or without the semantic layer
    related_pairs = skill_matcher.match_related(missing_skills, additional_skills)
    partial_skill_units = _consume_pairs(related_pairs, matched_skills, missing_skills, additional_skills)

    assessment = qualification_matcher.assess(
        resume.degree, resume.branch, jd.preferred_qualification, _jd_text(jd_id)
    )
    qualification_match = assessment.matched
    matching_reason = assessment.reason
    qualification_points = assessment.score

    experience_match = experience_matcher.match_experience(resume.experience_years, jd.experience)
    descriptive_experience = experience_matcher.is_descriptive_requirement(jd.experience)

    resume_text = " ".join(resume.achievements + resume.experience + resume.projects)
    matched_keywords = soft_skill_matcher.match_soft_skills(jd.keywords, resume_text)
    rule_keyword_covered = len(matched_keywords)

    semantic_keyword_units = 0
    if semantic_config.SEMANTIC_ENABLED:
        try:
            skill_hits = semantic_matcher.match_skills(missing_skills, additional_skills)
            partial_skill_units += _consume_pairs(
                [(jd_skill, resume_skill) for jd_skill, resume_skill, _ in skill_hits],
                matched_skills, missing_skills, additional_skills,
            )

            unmatched_keywords = [k for k in jd.keywords if k not in matched_keywords]
            keyword_hits = semantic_matcher.match_keywords(unmatched_keywords, resume_text)
            matched_keywords = matched_keywords + [k for k, _ in keyword_hits]
            semantic_keyword_units = len(keyword_hits)

            # only for stated requirements the rules scored zero
            if assessment.requirement_mentioned and assessment.mentioned_score == 0:
                resume_qual_text = " ".join(filter(None, [resume.degree, resume.branch, *resume.education]))
                ok, _ = semantic_matcher.qualification_matches(resume_qual_text, jd.preferred_qualification)
                if ok:
                    qualification_match = True
                    qualification_points = min(
                        qualification_matcher.QUALIFICATION_WEIGHT,
                        qualification_points + semantic_config.SEMANTIC_QUALIFICATION_SCORE,
                    )
                    matching_reason = "The qualification is semantically close to the job requirement."

            if descriptive_experience:
                ok, _ = semantic_matcher.experience_matches(
                    " ".join(resume.experience + resume.projects), jd.experience
                )
                experience_match = ok
        except Exception:
            logger.warning("Semantic layer unavailable; using rule-based results only.", exc_info=True)

    skill_credit = exact_skill_units + semantic_config.SEMANTIC_MATCH_WEIGHT * partial_skill_units
    soft_credit = rule_keyword_covered + semantic_config.SEMANTIC_MATCH_WEIGHT * semantic_keyword_units

    scores = score_calculator.calculate_scores(
        skill_credit,
        len(jd.required_skills),
        experience_match,
        qualification_points,
        soft_credit,
        len(jd.keywords),
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