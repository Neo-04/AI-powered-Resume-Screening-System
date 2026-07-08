import re
from typing import Dict, List, Optional

from backend.app.schemas.resume import ParsedResume
from backend.app.services.resume_service import get_resume
from backend.app.utils import parsing
from backend.app.utils import qualifications

# Optional structured storage 
structured_resume_store: dict[str, ParsedResume] = {}

# Unchanged — kept exactly as defined.
RESUME_SECTION_ALIASES = {
    "skills": [
        "skills", "technical skills", "key skills", "core competencies", "technologies",
    ],
    "education": [
        "education", "academics", "academic background", "qualifications",
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment",
        "internship", "internships", "work history",
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects",
    ],
    "achievements": [
        "achievements", "awards", "honors", "honours", "accomplishments",
        "extra curricular", "extracurricular", "activities", "competitions",
        "certifications", "awards and honors", "honors and awards",
    ],
}

# Extra words for common non-aliased sections, all displayed in achievements.
_EXTRA_ACHIEVEMENT_CUES = {
    "competitive", "programming", "coding", "dsa", "problem", "leetcode",
    "codeforces", "hackathon", "hackathons", "contest", "contests", "profiles",
    "positions", "responsibility", "responsibilities", "volunteer",
    "volunteering", "hobbies", "interests", "publications", "patents",
}

_HEADER_NORMALIZE_RE = re.compile(r"[^a-z& ]+")
_HEADER_STOPWORDS = {
    "and", "or", "of", "the", "in", "for", "to", "a", "an", "&", "with", "on", "my",
}

_HEADER_LOOKUP = {
    alias: canonical
    for canonical, aliases in RESUME_SECTION_ALIASES.items()
    for alias in aliases
}


def _build_category_keywords(aliases: Dict[str, List[str]]) -> Dict[str, str]:
    token_categories: Dict[str, set] = {}
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            for token in alias.split():
                token_categories.setdefault(token, set()).add(canonical)
    return {
        token: next(iter(cats))
        for token, cats in token_categories.items()
        if len(cats) == 1 and token not in _HEADER_STOPWORDS and len(token) >= 3
    }


#extra achievement cues are added to the category cues for achievements section
_CATEGORY_CUES: Dict[str, str] = {
    **{token: "achievements" for token in _EXTRA_ACHIEVEMENT_CUES},
    **_build_category_keywords(RESUME_SECTION_ALIASES),
}


def _normalize_header(line: str) -> str:
    cleaned = _HEADER_NORMALIZE_RE.sub(" ", line.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _category_from_cues(line: str) -> Optional[str]:
    for token in _normalize_header(line).split():
        category = _CATEGORY_CUES.get(token)
        if category:
            return category
    return None


def _is_bullet(line: str) -> bool:
    return parsing.clean_bullet(line) != line.strip()


def _looks_like_header(line: str) -> bool:
    #Rule-based heuristic for a section header (no ML)
    core = line.rstrip(":").strip()
    if not (1 <= len(core) <= 45):
        return False
    if "@" in core or any(ch.isdigit() for ch in core):
        return False
    if any(ch in core for ch in "().,;/|:"):
        return False
    words = core.split()
    if not (1 <= len(words) <= 6):
        return False
    alpha_words = [w for w in words if any(c.isalpha() for c in w)]
    if not alpha_words:
        return False
    significant = [w for w in alpha_words if w.lower() not in _HEADER_STOPWORDS] or alpha_words
    capitalised = sum(1 for w in significant if w[0].isupper())
    return capitalised / len(significant) >= 0.6


def _split_resume_sections(text: str) -> Dict[str, List[str]]:
    """Group lines under canonical sections.

    1. Exact alias match                       -> that category.
    2. Header-like and carries a section cue    -> that cue's category.
    3. Everything else                          -> content of current section."""
    sections: Dict[str, List[str]] = {"_preamble": []}
    current = "_preamble"

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if not _is_bullet(line):
            known = _HEADER_LOOKUP.get(_normalize_header(line))
            if known:
                current = known
                sections.setdefault(current, [])
                continue
            if _looks_like_header(line):
                category = _category_from_cues(line)
                if category:
                    current = category
                    sections.setdefault(current, [])
                    continue

        sections.setdefault(current, []).append(line)

    return sections


def parse_resume(resume_id: str) -> ParsedResume:
    resume = get_resume(resume_id)  # raises ResumeProcessingError(404) if missing
    text = resume.text

    sections = _split_resume_sections(text)

    skills_source = " ".join(sections.get("skills", [])) if sections.get("skills") else text

    education_text = " ".join(sections.get("education", []))

    parsed = ParsedResume(
        resume_id=resume_id,
        name=parsing.guess_name(parsing.to_lines(text)[:6]),
        skills=parsing.extract_skills(skills_source),
        education=parsing.section_items(sections.get("education", [])),
        experience=parsing.section_items(sections.get("experience", [])),
        projects=parsing.section_items(sections.get("projects", [])),
        achievements=parsing.summarize_items(sections.get("achievements", [])),
        degree=qualifications.first_degree(education_text),
        branch=qualifications.first_branch(education_text),
        experience_years=qualifications.years_of_experience(sections.get("experience", [])),
    )

    structured_resume_store[resume_id] = parsed
    return parsed