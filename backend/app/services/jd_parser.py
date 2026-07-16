import re
from typing import List

from backend.app.schemas.jd import ParsedJD
from backend.app.services.jd_service import get_job_description
from backend.app.utils import parsing, qualifications

structured_jd_store: dict[str, ParsedJD] = {}

JD_SECTION_ALIASES = {
    "required": [
        "required skills",
        "requirements",
        "must have",
        "required qualifications",
        "skills required",
        "key skills",
    ],
}

_ROLE_RE = re.compile(r"^(?:role|position|title|job title)\s*[:\-]\s*(.+)$", re.I)
_EXP_RE = re.compile(
    r"(\d+\+?\s*(?:-\s*\d+)?\s*(?:years|yrs|year))(?:\s+of\s+experience)?", re.I
)

_SOFT_SKILL_PATTERNS = [
    ("Communication", re.compile(r"\bcommunication\b", re.I)),
    ("Leadership", re.compile(r"\bleadership\b", re.I)),
    ("Teamwork", re.compile(r"\bteam\s?work\b", re.I)),
    ("Collaboration", re.compile(r"\bcollaborat(?:ion|ive)\b", re.I)),
    ("Problem-solving", re.compile(r"\bproblem[\s-]?solving\b", re.I)),
    ("Analytical thinking", re.compile(r"\banalytical(?:\s+thinking)?\b", re.I)),
    ("Critical thinking", re.compile(r"\bcritical\s+thinking\b", re.I)),
    ("Stakeholder management", re.compile(r"\bstakeholder\s+management\b", re.I)),
    ("Adaptability", re.compile(r"\badaptab(?:ility|le)\b", re.I)),
    ("Presentation skills", re.compile(r"\bpresentation(?:\s+skills)?\b", re.I)),
    ("Time management", re.compile(r"\btime\s+management\b", re.I)),
    (
        "Business understanding",
        re.compile(r"\bbusiness\s+(?:understanding|acumen)\b", re.I),
    ),
    ("Customer focus", re.compile(r"\bcustomer\s+(?:focus|centric)\b", re.I)),
    ("Interpersonal skills", re.compile(r"\binterpersonal\b", re.I)),
    ("Attention to detail", re.compile(r"\battention\s+to\s+detail\b", re.I)),
    ("Creativity", re.compile(r"\bcreativ(?:ity|e)\b", re.I)),
    ("Negotiation", re.compile(r"\bnegotiation\b", re.I)),
    ("Mentoring", re.compile(r"\bmentor(?:ing|ship)?\b", re.I)),
    ("Decision-making", re.compile(r"\bdecision[\s-]?making\b", re.I)),
    ("Organization", re.compile(r"\borgani[sz]ational?\b", re.I)),
    ("Multitasking", re.compile(r"\bmulti[\s-]?tasking\b", re.I)),
    ("Ownership", re.compile(r"\bownership\b", re.I)),
]


def _extract_role(text: str) -> str:
    lines = parsing.to_lines(text)
    for line in lines[:8]:
        m = _ROLE_RE.match(line)
        if m:
            return m.group(1).strip()
    for line in lines[:3]:
        if 2 <= len(line.split()) <= 8 and "@" not in line:
            return line
    return ""


def _extract_experience(text: str) -> str:
    m = _EXP_RE.search(text)
    return m.group(0).strip() if m else ""


def _extract_soft_skills(text: str, exclude: List[str]) -> List[str]:
    excluded = {e.lower() for e in exclude}
    found, seen = [], set()
    for display, pattern in _SOFT_SKILL_PATTERNS:
        key = display.lower()
        if key in seen or key in excluded:
            continue
        if pattern.search(text):
            found.append(display)
            seen.add(key)
    return found


def parse_jd(jd_id: str) -> ParsedJD:
    jd = get_job_description(jd_id)
    text = jd.text

    sections = parsing.split_sections(text, JD_SECTION_ALIASES)
    required_source = " ".join(sections.get("required", [])) or text
    required_skills = parsing.extract_skills(required_source)

    parsed = ParsedJD(
        jd_id=jd_id,
        role=_extract_role(text),
        required_skills=required_skills,
        preferred_qualification=qualifications.extract_qualifications(text),
        experience=_extract_experience(text),
        keywords=_extract_soft_skills(text, exclude=required_skills),
    )

    structured_jd_store[jd_id] = parsed
    return parsed
