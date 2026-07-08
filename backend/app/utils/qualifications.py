import re
from collections import namedtuple
from typing import List, Optional, Tuple


def _c(pattern: str, ignore_case: bool = True) -> "re.Pattern":
    return re.compile(pattern, re.I if ignore_case else 0)


DegreeId = namedtuple("DegreeId", "group level generic")

# specific displays before generic ones
_DEGREE_PATTERNS = [
    ("B.Tech", _c(r"\b(?:B\.?\s?Tech|Bachelor of Technology)\b")),
    ("B.E.", _c(r"\b(?:B\.E\.?|Bachelor of Engineering)\b")),
    ("M.Tech", _c(r"\b(?:M\.?\s?Tech|Master of Technology)\b")),
    ("M.E.", _c(r"\b(?:M\.E\.?|Master of Engineering)\b")),
    ("M.Sc", _c(r"\b(?:M\.?Sc|Master of Science)\b")),
    ("B.Sc", _c(r"\b(?:B\.?Sc|Bachelor of Science)\b")),
    ("M.Com", _c(r"\b(?:M\.?Com|Master of Commerce)\b")),
    ("B.Com", _c(r"\b(?:B\.?Com|Bachelor of Commerce)\b")),
    ("MCA", _c(r"\bMCA\b", False)),
    ("BCA", _c(r"\bBCA\b", False)),
    ("MBA", _c(r"\bMBA\b", False)),
    ("PhD", _c(r"\b(?:Ph\.?D\.?|Doctorate)\b")),
    ("MA", _c(r"\b(?:MA|M\.A\.?|Master of Arts)\b", False)),
    ("BA", _c(r"\b(?:BA|B\.A\.?|Bachelor of Arts)\b", False)),
    ("Master's", _c(r"\bMaster(?:'s|s)?(?: Degree)?\b")),
    ("Bachelor's", _c(r"\bBachelor(?:'s|s)?(?: Degree)?\b")),
    ("Diploma", _c(r"\bDiploma\b")),
]

# equivalent groups
_DEGREE_GROUPS = {
    "M.Tech": DegreeId("engineering-master", "master", False),
    "M.E.": DegreeId("engineering-master", "master", False),
    "B.Tech": DegreeId("engineering-bachelor", "bachelor", False),
    "B.E.": DegreeId("engineering-bachelor", "bachelor", False),
    "M.Sc": DegreeId("science-master", "master", False),
    "B.Sc": DegreeId("science-bachelor", "bachelor", False),
    "M.Com": DegreeId("commerce-master", "master", False),
    "B.Com": DegreeId("commerce-bachelor", "bachelor", False),
    "MA": DegreeId("arts-master", "master", False),
    "BA": DegreeId("arts-bachelor", "bachelor", False),
    "MCA": DegreeId("mca", "master", False),
    "BCA": DegreeId("bca", "bachelor", False),
    "MBA": DegreeId("mba", "master", False),
    "PhD": DegreeId("doctorate", "doctorate", False),
    "Diploma": DegreeId("diploma", "diploma", False),
    "Master's": DegreeId("__generic_master__", "master", True),
    "Bachelor's": DegreeId("__generic_bachelor__", "bachelor", True),
}

_BRANCH_PATTERNS = [
    ("Electronics and Communication Engineering", _c(r"\bElectronics and Communication(?: Engineering)?\b")),
    ("Electronics and Communication Engineering", _c(r"\bECE\b", False)),
    ("Electrical Engineering", _c(r"\bElectrical(?: and Electronics)?(?: Engineering)?\b")),
    ("Electrical Engineering", _c(r"\b(?:EEE|EE)\b", False)),
    ("Computer Science", _c(r"\bComputer Science(?: and Engineering)?\b")),
    ("Computer Science", _c(r"\b(?:CSE|CS)\b", False)),
    ("Information Technology", _c(r"\bInformation Technology\b")),
    ("Information Technology", _c(r"\bIT\b", False)),
    ("Software Engineering", _c(r"\bSoftware Engineering\b")),
    ("Data Science", _c(r"\bData Science\b")),
    ("Data Science", _c(r"\bDS\b", False)),
    ("Artificial Intelligence", _c(r"\bArtificial Intelligence\b")),
    ("Artificial Intelligence", _c(r"\b(?:AIML|AI)\b", False)),
    ("Computer Engineering", _c(r"\bComputer Engineering\b")),
    ("Mechanical Engineering", _c(r"\bMechanical(?: Engineering)?\b")),
    ("Civil Engineering", _c(r"\bCivil(?: Engineering)?\b")),
    ("Statistics", _c(r"\bStatistics\b")),
    ("Mathematics", _c(r"\b(?:Mathematics|Maths)\b")),
]

# Related-branch 
RELATED_BRANCHES = {
    "Computer Science": {
        "Information Technology", "Software Engineering", "Data Science",
        "Artificial Intelligence", "Computer Engineering",
    },
    "Electrical Engineering": {"Electronics and Communication Engineering"},
    "Electronics and Communication Engineering": {"Electrical Engineering"},
}


def _first(patterns, text: str) -> str:
    for canonical, pattern in patterns:
        if pattern.search(text):
            return canonical
    return ""


def first_degree(text: str) -> str:
    return _first(_DEGREE_PATTERNS, text)


def canonical_branch(text: str) -> str:
    return _first(_BRANCH_PATTERNS, text)


first_branch = canonical_branch  # display + comparison share one canonical form


def canonical_degree(text: str) -> Optional[DegreeId]:
    return _DEGREE_GROUPS.get(first_degree(text))


def degrees_equivalent(resume: Optional[DegreeId], jd: Optional[DegreeId]) -> bool:
    if not resume or not jd:
        return False
    if jd.generic:  # generic requirement -> any degree of the same level
        return resume.level == jd.level
    return resume.group == jd.group  # specific requirement -> same equivalence group


def is_related_branch(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a == b:
        return True
    return b in RELATED_BRANCHES.get(a, set()) or a in RELATED_BRANCHES.get(b, set())


def split_jd_qualifications(items: List[str]) -> Tuple[List[DegreeId], List[str]]:
    degrees, branches = [], []
    for item in items:
        degree = canonical_degree(item)
        if degree and degree not in degrees:
            degrees.append(degree)
        branch = canonical_branch(item)
        if branch and branch not in branches:
            branches.append(branch)
    return degrees, branches


def years_of_experience(lines: List[str]) -> float:
    text = " ".join(lines).lower()
    if not text.strip():
        return 0.0
    years = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)", text)]
    months = [float(x) / 12 for x in re.findall(r"(\d+)\s*(?:months|month|mos)\b", text)]
    return round(max(years + months + [0.0]), 1)