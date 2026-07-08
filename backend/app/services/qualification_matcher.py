from typing import Dict, List, Tuple

from backend.app.utils import qualifications

_NO_MATCH_REASON = "The candidate's educational qualification does not satisfy the job requirements."
_QUALIFICATION_WEIGHT = 15  # cap; matches the qualification weight in score_calculator


def _evaluate(resume_degree: str, resume_branch: str, jd_qualifications: List[str]) -> Dict[str, bool]:
    jd_degrees, jd_branches = qualifications.split_jd_qualifications(jd_qualifications)
    resume_deg = qualifications.canonical_degree(resume_degree)
    resume_br = qualifications.canonical_branch(resume_branch)

    has_degree_req, has_branch_req = bool(jd_degrees), bool(jd_branches)

    specific_degree = has_degree_req and any(
        (not d.generic) and qualifications.degrees_equivalent(resume_deg, d) for d in jd_degrees
    )
    generic_degree = has_degree_req and not specific_degree and any(
        d.generic and qualifications.degrees_equivalent(resume_deg, d) for d in jd_degrees
    )
    branch_exact = has_branch_req and bool(resume_br) and resume_br in jd_branches
    branch_related = (
        has_branch_req and not branch_exact and bool(resume_br)
        and any(qualifications.is_related_branch(resume_br, b) for b in jd_branches)
    )
    return {
        "has_degree_req": has_degree_req,
        "has_branch_req": has_branch_req,
        "specific_degree": specific_degree,
        "generic_degree": generic_degree,
        "degree_match": specific_degree or generic_degree,
        "branch_exact": branch_exact,
        "branch_related": branch_related,
    }


def match_qualification(resume_degree: str, resume_branch: str, jd_qualifications: List[str]) -> Tuple[bool, str]:
    s = _evaluate(resume_degree, resume_branch, jd_qualifications)
    degree_match, branch_exact, branch_related = s["degree_match"], s["branch_exact"], s["branch_related"]
    has_degree_req, has_branch_req = s["has_degree_req"], s["has_branch_req"]

    matched = degree_match or branch_exact or branch_related or (not has_degree_req and not has_branch_req)
    if not has_degree_req and has_branch_req:
        matched = branch_exact or branch_related

    if not matched:
        return False, _NO_MATCH_REASON

    if degree_match and branch_exact:
        reason = "Both the degree and branch satisfy the job requirements."
    elif degree_match and branch_related:
        reason = "The degree satisfies the requirement, and the branch is different but closely related."
    elif degree_match and has_branch_req:
        reason = "The degree satisfies the requirement, but the branch is different."
    elif degree_match:
        reason = "The degree satisfies the requirement."
    elif branch_related:
        reason = "The degree is different, but the branch is closely related to the required field."
    elif branch_exact:
        reason = "The branch satisfies the requirement, but the degree is different."
    else:
        reason = "The qualification satisfies the job requirements."
    return True, reason


def qualification_score(resume_degree: str, resume_branch: str, jd_qualifications: List[str]) -> int:
    s = _evaluate(resume_degree, resume_branch, jd_qualifications)
    has_degree_req, has_branch_req = s["has_degree_req"], s["has_branch_req"]
    specific, generic = s["specific_degree"], s["generic_degree"]
    branch_exact, branch_related = s["branch_exact"], s["branch_related"]

    # no degree required -> branch (or nothing) drives the score
    if not has_degree_req:
        if not has_branch_req or branch_exact:
            return _QUALIFICATION_WEIGHT
        return 13 if branch_related else 0

    # specific degree match
    if specific:
        if not has_branch_req or branch_exact:
            return _QUALIFICATION_WEIGHT
        return 14 if branch_related else 12

    # generic degree match
    if generic:
        if not has_branch_req or branch_exact:
            return 11
        return 10 if branch_related else 9

    # degree not matched -> branch only
    if branch_exact:
        return 8
    if branch_related:
        return 6
    return 0