import re
from collections import namedtuple
from typing import Dict, List, Tuple

from backend.app.utils import qualifications

_NO_MATCH_REASON = (
    "The candidate's educational qualification does not satisfy the job requirements."
)
_NOT_SPECIFIED_REASON = (
    "The job description does not specify a qualification requirement."
)

QUALIFICATION_WEIGHT = 15
_DEGREE_POINTS = 9
_BRANCH_POINTS = 6

_SPECIFIC_DEGREE_POINTS = 9
_GENERIC_DEGREE_POINTS = 6
_EXACT_BRANCH_POINTS = 6
_RELATED_BRANCH_POINTS = 4

DEGREE_AND_BRANCH = "degree_and_branch"
DEGREE_ONLY = "degree_only"
BRANCH_ONLY = "branch_only"
GENERIC_RELEVANT_FIELD = "generic_relevant_field"
PREFERRED_ONLY = "preferred_only"
NOT_MENTIONED = "not_mentioned"

QualificationAssessment = namedtuple(
    "QualificationAssessment",
    "degree_score branch_score score category matched reason requirement_mentioned mentioned_score",
)

_PREFERRED_CUE_RE = re.compile(
    r"\b(?:preferred|preferable|preferably|desirable|desired|nice to have|good to have|a plus|is a plus|plus point|bonus)\b",
    re.I,
)
_RELEVANT_FIELD_RE = re.compile(
    r"\b(?:relevant|related|similar|any|equivalent)\s+(?:technical\s+|quantitative\s+|engineering\s+)?"
    r"(?:field|discipline|stream|branch|background|domain|subject)\b",
    re.I,
)
_DEGREE_WORD_RE = re.compile(r"\b(?:degree|graduation|graduate|qualification)\b", re.I)


def _evaluate(
    resume_degree: str, resume_branch: str, jd_qualifications: List[str]
) -> Dict[str, bool]:
    jd_degrees, jd_branches = qualifications.split_jd_qualifications(jd_qualifications)
    resume_deg = qualifications.canonical_degree(resume_degree)
    resume_br = qualifications.canonical_branch(resume_branch)

    has_degree_req, has_branch_req = bool(jd_degrees), bool(jd_branches)

    specific_degree = has_degree_req and any(
        (not d.generic) and qualifications.degrees_equivalent(resume_deg, d)
        for d in jd_degrees
    )
    generic_degree = (
        has_degree_req
        and not specific_degree
        and any(
            d.generic and qualifications.degrees_equivalent(resume_deg, d)
            for d in jd_degrees
        )
    )
    branch_exact = has_branch_req and bool(resume_br) and resume_br in jd_branches
    branch_related = (
        has_branch_req
        and not branch_exact
        and bool(resume_br)
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
        "has_resume_degree": bool(resume_deg),
        "has_resume_branch": bool(resume_br),
    }


def _qualification_context(jd_qualifications: List[str], jd_text: str) -> str:
    # JD lines that actually carry a qualification signal.

    # Scanning the whole JD would pick up unrelated cues such as a 'Preferred Skills' heading.
    lines = [line.strip() for line in (jd_text or "").splitlines() if line.strip()]
    relevant = [
        line
        for line in lines
        if qualifications.first_degree(line)
        or qualifications.canonical_branch(line)
        or _RELEVANT_FIELD_RE.search(line)
    ]
    return " ".join(relevant) if relevant else " ".join(jd_qualifications)


def _classify(signals: Dict[str, bool], generic_field: bool, preferred: bool) -> str:
    has_degree_req, has_branch_req = (
        signals["has_degree_req"],
        signals["has_branch_req"],
    )

    if not has_degree_req and not has_branch_req:
        return GENERIC_RELEVANT_FIELD if generic_field else NOT_MENTIONED
    if preferred:
        return PREFERRED_ONLY
    if has_degree_req and has_branch_req:
        return DEGREE_AND_BRANCH
    return DEGREE_ONLY if has_degree_req else BRANCH_ONLY


def _degree_points(signals: Dict[str, bool]) -> int:
    if signals["specific_degree"]:
        return _SPECIFIC_DEGREE_POINTS
    if signals["generic_degree"]:
        return _GENERIC_DEGREE_POINTS
    return 0


def _branch_points(signals: Dict[str, bool]) -> int:
    if signals["branch_exact"]:
        return _EXACT_BRANCH_POINTS
    if signals["branch_related"]:
        return _RELATED_BRANCH_POINTS
    return 0


def _reason(signals: Dict[str, bool], category: str, matched: bool) -> str:
    if category == NOT_MENTIONED:
        return _NOT_SPECIFIED_REASON
    if not matched:
        return _NO_MATCH_REASON
    if category == GENERIC_RELEVANT_FIELD:
        return "The candidate holds a degree in a relevant field."

    degree_match = signals["degree_match"]
    branch_exact, branch_related = signals["branch_exact"], signals["branch_related"]
    has_branch_req = signals["has_branch_req"]

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

    if category == PREFERRED_ONLY:
        return reason + " The qualification is preferred rather than mandatory."
    return reason


def assess(
    resume_degree: str,
    resume_branch: str,
    jd_qualifications: List[str],
    jd_text: str = "",
) -> QualificationAssessment:
    # Qualification is out of 15: degree 9 + branch 6.

    # A component the JD never states earns full credit, so an incomplete JD is not treated as a candidate mismatch.

    signals = _evaluate(resume_degree, resume_branch, jd_qualifications)
    context = _qualification_context(jd_qualifications, jd_text)
    generic_field = bool(_RELEVANT_FIELD_RE.search(context))
    preferred = bool(_PREFERRED_CUE_RE.search(context))
    category = _classify(signals, generic_field, preferred)

    if signals["has_degree_req"]:
        degree_score = _degree_points(signals)
    else:
        degree_score = _DEGREE_POINTS

    branch_required = signals["has_branch_req"] or generic_field
    if signals["has_branch_req"]:
        branch_score = _branch_points(signals)
    elif generic_field:
        branch_score = _BRANCH_POINTS if signals["has_resume_branch"] else 0
    else:
        branch_score = _BRANCH_POINTS

    mentioned_score = 0
    if signals["has_degree_req"]:
        mentioned_score += degree_score
    if branch_required:
        mentioned_score += branch_score
    requirement_mentioned = signals["has_degree_req"] or branch_required

    matched = True if not requirement_mentioned else mentioned_score > 0
    score = degree_score + branch_score

    return QualificationAssessment(
        degree_score,
        branch_score,
        score,
        category,
        matched,
        _reason(signals, category, matched),
        requirement_mentioned,
        mentioned_score,
    )


def match_qualification(
    resume_degree: str,
    resume_branch: str,
    jd_qualifications: List[str],
    jd_text: str = "",
) -> Tuple[bool, str]:
    assessment = assess(resume_degree, resume_branch, jd_qualifications, jd_text)
    return assessment.matched, assessment.reason


def qualification_score(
    resume_degree: str,
    resume_branch: str,
    jd_qualifications: List[str],
    jd_text: str = "",
) -> int:
    return assess(resume_degree, resume_branch, jd_qualifications, jd_text).score
