import re
from typing import Dict, Iterable, List, Optional

_BULLET_RE = re.compile(r"^[\s\-\u2022\u25CF\u25AA\u2023\u2043*•·▪◦‣]+")


def clean_bullet(line: str) -> str:
    return _BULLET_RE.sub("", line).strip()


def to_lines(text: str) -> List[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


_HEADER_NORMALIZE_RE = re.compile(r"[^a-z& ]+")


def _normalize_header(line: str) -> str:
    cleaned = _HEADER_NORMALIZE_RE.sub(" ", line.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _match_header(line: str, header_lookup: Dict[str, str]) -> Optional[str]:
    if len(line) > 45:
        return None
    return header_lookup.get(_normalize_header(line))


def split_sections(text: str, aliases: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Group lines under canonical section names.

    `aliases` maps canonical name -> list of lowercase header keywords.
    Lines before the first recognized header land under "_preamble".
    """
    header_lookup: Dict[str, str] = {}
    for canonical, keys in aliases.items():
        for k in keys:
            header_lookup[k] = canonical

    sections: Dict[str, List[str]] = {"_preamble": []}
    current = "_preamble"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        canonical = _match_header(line, header_lookup)
        if canonical:
            current = canonical
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


SKILL_KEYWORDS: List[str] = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "Golang",
    "Rust",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "Scala",
    "MATLAB",
    "SQL",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "Django",
    "Flask",
    "FastAPI",
    "Spring",
    ".NET",
    "Machine Learning",
    "ML",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "AI",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Kubernetes",
    "Git",
    "Linux",
    "Jenkins",
    "CI/CD",
    "MongoDB",
    "PostgreSQL",
    "MySQL",
    "Redis",
    "Kafka",
    "Spark",
    "Hadoop",
    "REST",
    "GraphQL",
    "Microservices",
    "Tableau",
    "Power BI",
    "Excel",
]


def extract_skills(text: str, extra: Iterable[str] = ()) -> List[str]:
    lowered = text.lower()
    found: List[str] = []
    seen = set()
    for kw in list(SKILL_KEYWORDS) + list(extra):
        key = kw.lower()
        if key in seen:
            continue
        pattern = r"(?<![a-z0-9+#.])" + re.escape(key) + r"(?![a-z0-9+#.])"
        if re.search(pattern, lowered):
            found.append(kw)
            seen.add(key)
    return found


def section_items(lines: List[str], max_items: int = 25) -> List[str]:
    items: List[str] = []
    for line in lines:
        cleaned = clean_bullet(line)
        if len(cleaned) < 3:
            continue
        items.append(cleaned)
        if len(items) >= max_items:
            break
    return items


def summarize_items(
    lines: List[str], max_items: int = 10, max_len: int = 140
) -> List[str]:
    out: List[str] = []
    for line in lines:
        cleaned = clean_bullet(line)
        if len(cleaned) < 4:
            continue
        first = re.split(r"(?<=[.!?])\s+", cleaned)[0]
        if len(first) > max_len:
            first = first[:max_len].rsplit(" ", 1)[0] + "…"
        out.append(first)
        if len(out) >= max_items:
            break
    return out


def _looks_like_name(s: str) -> bool:
    if not s or "@" in s or any(ch.isdigit() for ch in s) or len(s) > 40:
        return False
    words = s.split()
    if not (2 <= len(words) <= 4):
        return False
    if not all(re.fullmatch(r"[A-Za-z.'\-]+", w) for w in words):
        return False
    caps = sum(1 for w in words if w[:1].isupper())
    return caps >= len(words) - 1


def guess_name(preamble_lines: List[str]) -> str:
    for line in preamble_lines[:5]:
        candidate = clean_bullet(line)
        if _looks_like_name(candidate):
            return candidate
    return ""
