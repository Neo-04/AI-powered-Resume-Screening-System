import re
from typing import List

from backend.app.schemas.jd import ParsedJD
from backend.app.services.jd_service import get_job_description
from backend.app.utils import parsing

# Optional structured storage (Phase 3 output cache).
structured_jd_store: dict[str, ParsedJD] = {}

JD_SECTION_ALIASES = {
    "required": [
        "required skills", "requirements", "must have", "required qualifications",
        "skills required", "key skills",
    ],
}

_ROLE_RE = re.compile(r"^(?:role|position|title|job title)\s*[:\-]\s*(.+)$", re.I)
_EXP_RE = re.compile(
    r"(\d+\+?\s*(?:-\s*\d+)?\s*(?:years|yrs|year))(?:\s+of\s+experience)?", re.I
)

# Academic qualifications: degrees + branches/streams. Ambiguous tokens
# (BE, IT, ECE, ...) are matched case-sensitively to avoid false positives
# like the word "be" or "it".
_QUALIFICATION_PATTERNS = [
    ("B.Tech", re.compile(r"\bB\.?\s?Tech\b", re.I)),
    ("M.Tech", re.compile(r"\bM\.?\s?Tech\b", re.I)),
    ("B.E.", re.compile(r"\bB\.E\.?\b", re.I)),
    ("M.E.", re.compile(r"\bM\.E\.?\b", re.I)),
    ("B.Sc", re.compile(r"\bB\.?Sc\b", re.I)),
    ("M.Sc", re.compile(r"\bM\.?Sc\b", re.I)),
    ("BCA", re.compile(r"\bBCA\b")),
    ("MCA", re.compile(r"\bMCA\b")),
    ("MBA", re.compile(r"\bMBA\b")),
    ("PhD", re.compile(r"\bPh\.?D\.?\b", re.I)),
    ("Bachelor's", re.compile(r"\bBachelor(?:'s|s)?\b", re.I)),
    ("Master's", re.compile(r"\bMaster(?:'s|s)?\b", re.I)),
    ("Diploma", re.compile(r"\bDiploma\b", re.I)),
    ("Computer Science", re.compile(r"\bComputer Science\b", re.I)),
    ("CSE", re.compile(r"\bCSE\b")),
    ("Information Technology", re.compile(r"\bInformation Technology\b", re.I)),
    ("IT", re.compile(r"\bIT\b")),
    ("ECE", re.compile(r"\bECE\b")),
    ("EEE", re.compile(r"\bEEE\b")),
    ("Electronics", re.compile(r"\bElectronics\b", re.I)),
    ("Electrical", re.compile(r"\bElectrical\b", re.I)),
    ("Mechanical", re.compile(r"\bMechanical\b", re.I)),
    ("Civil", re.compile(r"\bCivil\b", re.I)),
    ("Data Science", re.compile(r"\bData Science\b", re.I)),
    ("Artificial Intelligence", re.compile(r"\bArtificial Intelligence\b", re.I)),
    ("Statistics", re.compile(r"\bStatistics\b", re.I)),
    ("Mathematics", re.compile(r"\bMathematics\b", re.I)),
    ("Software Engineering", re.compile(r"\bSoftware Engineering\b", re.I)),
]

# Non-technical / soft-skill cues for `keywords`.
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
    ("Business understanding", re.compile(r"\bbusiness\s+(?:understanding|acumen)\b", re.I)),
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


def _extract_qualifications(text: str) -> List[str]:
    found: List[str] = []
    seen = set()
    for display, pattern in _QUALIFICATION_PATTERNS:
        if display not in seen and pattern.search(text):
            found.append(display)
            seen.add(display)
    return found


def _extract_soft_skills(text: str, exclude: List[str]) -> List[str]:
    excluded = {e.lower() for e in exclude}
    found: List[str] = []
    seen = set()
    for display, pattern in _SOFT_SKILL_PATTERNS:
        key = display.lower()
        if key in seen or key in excluded:
            continue
        if pattern.search(text):
            found.append(display)
            seen.add(key)
    return found


def parse_jd(jd_id: str) -> ParsedJD:
    jd = get_job_description(jd_id)  # raises JDProcessingError(404) if missing
    text = jd.text

    sections = parsing.split_sections(text, JD_SECTION_ALIASES)
    required_source = " ".join(sections.get("required", [])) or text
    required_skills = parsing.extract_skills(required_source)

    parsed = ParsedJD(
        jd_id=jd_id,
        role=_extract_role(text),
        required_skills=required_skills,
        preferred_qualification=_extract_qualifications(text),
        experience=_extract_experience(text),
        keywords=_extract_soft_skills(text, exclude=required_skills),
    )

    structured_jd_store[jd_id] = parsed
    return parsed