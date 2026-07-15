from typing import List, Tuple

from backend.app.utils.skills_normalizer import are_related_skills, canonical_skill


def _dedupe(skills: List[str]) -> List[str]:
    seen, out = set(), []
    for skill in skills:
        key = canonical_skill(skill)
        if key not in seen:
            seen.add(key)
            out.append(skill)
    return out


def match_skills(resume_skills: List[str], required_skills: List[str]) -> Tuple[List[str], List[str], List[str]]:
    required_canonical = {canonical_skill(s) for s in required_skills}
    resume_canonical = {canonical_skill(s) for s in resume_skills}

    matched = _dedupe([s for s in resume_skills if canonical_skill(s) in required_canonical])
    missing = _dedupe([s for s in required_skills if canonical_skill(s) not in resume_canonical])
    additional = _dedupe([s for s in resume_skills if canonical_skill(s) not in required_canonical])
    return matched, missing, additional


def match_related(missing_required: List[str], unmatched_resume: List[str]) -> List[Tuple[str, str]]:
    """Pair each unmatched JD skill with a related resume skill.

    A resume skill is consumed by the first pairing it satisfies.
    """
    pairs: List[Tuple[str, str]] = []
    consumed = set()
    for jd_skill in missing_required:
        for resume_skill in unmatched_resume:
            if resume_skill in consumed:
                continue
            if are_related_skills(jd_skill, resume_skill):
                pairs.append((jd_skill, resume_skill))
                consumed.add(resume_skill)
                break
    return pairs