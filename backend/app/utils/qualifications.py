import re
from collections import namedtuple
from typing import List, Optional, Tuple


def _c(pattern: str, ignore_case: bool = True) -> "re.Pattern":
    return re.compile(pattern, re.I if ignore_case else 0)


DegreeId = namedtuple("DegreeId", "group level generic")

# specific degrees before generic ones; order decides which display wins
_DEGREE_PATTERNS = [
    ("M.Tech", _c(r"\b(?:M\.?\s?Tech|Master of Technology)\b")),
    ("B.Tech", _c(r"\b(?:B\.?\s?Tech|Bachelor of Technology)\b")),
    ("M.E.", _c(r"\b(?:M\.E\.?|Master of Engineering)\b")),
    ("B.E.", _c(r"\b(?:B\.E\.?|Bachelor of Engineering)\b")),
    ("M.Sc", _c(r"\b(?:M\.?\s?Sc|Master of Science)\b")),
    ("B.Sc", _c(r"\b(?:B\.?\s?Sc|Bachelor of Science)\b")),
    ("M.Com", _c(r"\b(?:M\.?\s?Com|Master of Commerce)\b")),
    ("B.Com", _c(r"\b(?:B\.?\s?Com|Bachelor of Commerce)\b")),
    ("MBA", _c(r"\b(?:MBA|Master of Business Administration)\b")),
    ("BBA", _c(r"\b(?:BBA|Bachelor of Business Administration)\b")),
    ("MCA", _c(r"\b(?:MCA|Master of Computer Applications?)\b")),
    ("BCA", _c(r"\b(?:BCA|Bachelor of Computer Applications?)\b")),
    ("PhD", _c(r"\b(?:Ph\.?\s?D\.?|Doctorate|Doctor of Philosophy)\b")),
    ("MA", _c(r"\b(?:M\.A\.?|Master of Arts)\b")),
    ("BA", _c(r"\b(?:B\.A\.?|Bachelor of Arts)\b")),
    ("Master's", _c(r"\bMaster(?:'s|s)?(?: Degree)?\b")),
    ("Bachelor's", _c(r"\bBachelor(?:'s|s)?(?: Degree)?\b")),
    ("Diploma", _c(r"\bDiploma\b")),
]

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
    "MCA": DegreeId("computer-applications-master", "master", False),
    "BCA": DegreeId("computer-applications-bachelor", "bachelor", False),
    "MBA": DegreeId("business-master", "master", False),
    "BBA": DegreeId("business-bachelor", "bachelor", False),
    "PhD": DegreeId("doctorate", "doctorate", False),
    "Diploma": DegreeId("diploma", "diploma", False),
    "Master's": DegreeId("__generic_master__", "master", True),
    "Bachelor's": DegreeId("__generic_bachelor__", "bachelor", True),
}

# longer / more specific phrases first; abbreviations matched case-sensitively
_BRANCH_PATTERNS = [
    (
        "Electronics and Communication Engineering",
        _c(
            r"\b(?:Electronics and Communication|Electronics and Telecommunication)(?: Engineering)?\b"
        ),
    ),
    (
        "Electronics and Communication Engineering",
        _c(r"\bElectronics(?: Engineering)?\b"),
    ),
    ("Electronics and Communication Engineering", _c(r"\bECE\b", False)),
    (
        "Electrical Engineering",
        _c(r"\bElectrical(?: and Electronics)?(?: Engineering)?\b"),
    ),
    ("Electrical Engineering", _c(r"\b(?:EEE|EE)\b", False)),
    ("Instrumentation Engineering", _c(r"\bInstrumentation(?: Engineering)?\b")),
    ("Computer Science", _c(r"\bComputer Science(?: and Engineering)?\b")),
    ("Computer Science", _c(r"\b(?:CSE|CS)\b", False)),
    ("Computer Engineering", _c(r"\bComputer Engineering\b")),
    ("Information Technology", _c(r"\bInformation Technology\b")),
    ("Information Technology", _c(r"\bIT\b", False)),
    ("Software Engineering", _c(r"\bSoftware Engineering\b")),
    ("Data Science", _c(r"\bData Science\b")),
    ("Data Science", _c(r"\bDS\b", False)),
    ("Artificial Intelligence", _c(r"\bArtificial Intelligence\b")),
    ("Artificial Intelligence", _c(r"\b(?:AIML|AI)\b", False)),
    ("Machine Learning", _c(r"\bMachine Learning\b")),
    ("Aerospace Engineering", _c(r"\b(?:Aerospace|Aeronautical)(?: Engineering)?\b")),
    ("Automobile Engineering", _c(r"\b(?:Automobile|Automotive)(?: Engineering)?\b")),
    (
        "Production Engineering",
        _c(r"\b(?:Production|Industrial|Manufacturing)(?: Engineering)?\b"),
    ),
    ("Mechanical Engineering", _c(r"\bMechanical(?: Engineering)?\b")),
    ("Civil Engineering", _c(r"\bCivil(?: Engineering)?\b")),
    ("Architecture", _c(r"\bArchitecture\b")),
    ("Chemical Engineering", _c(r"\bChemical(?: Engineering)?\b")),
    (
        "Biotechnology",
        _c(r"\b(?:Biotechnology|Bioengineering|Biomedical(?: Engineering)?)\b"),
    ),
    ("Chemistry", _c(r"\bChemistry\b")),
    ("Physics", _c(r"\bPhysics\b")),
    ("Mathematics", _c(r"\b(?:Mathematics|Maths|Math)\b")),
    ("Statistics", _c(r"\b(?:Statistics|Statistical)\b")),
    ("Economics", _c(r"\bEconomics\b")),
    ("Finance", _c(r"\b(?:Finance|Financial Management)\b")),
    ("Accounting", _c(r"\b(?:Accounting|Accountancy)\b")),
    (
        "Business Administration",
        _c(r"\b(?:Business Administration|Business Management|Management Studies)\b"),
    ),
    ("Marketing", _c(r"\bMarketing\b")),
    ("Human Resources", _c(r"\b(?:Human Resources?|HR)\b")),
    ("Commerce", _c(r"\bCommerce\b")),
    ("Psychology", _c(r"\bPsychology\b")),
    ("Design", _c(r"\bDesign\b")),
]

# fields inside a group count as closely related; extend by adding to a group
_RELATED_BRANCH_GROUPS = [
    {
        "Computer Science",
        "Information Technology",
        "Software Engineering",
        "Computer Engineering",
        "Data Science",
        "Artificial Intelligence",
        "Machine Learning",
    },
    {
        "Electrical Engineering",
        "Electronics and Communication Engineering",
        "Instrumentation Engineering",
    },
    {
        "Mechanical Engineering",
        "Automobile Engineering",
        "Aerospace Engineering",
        "Production Engineering",
    },
    {"Civil Engineering", "Architecture"},
    {"Mathematics", "Statistics", "Data Science"},
    {"Commerce", "Finance", "Accounting", "Business Administration", "Economics"},
    {"Business Administration", "Marketing", "Human Resources"},
    {"Chemical Engineering", "Chemistry", "Biotechnology"},
]

RELATED_BRANCHES = {}
for _group in _RELATED_BRANCH_GROUPS:
    for _branch in _group:
        RELATED_BRANCHES.setdefault(_branch, set()).update(_group - {_branch})


def _first(patterns, text: str) -> str:
    for canonical, pattern in patterns:
        if pattern.search(text):
            return canonical
    return ""


def first_degree(text: str) -> str:
    return _first(_DEGREE_PATTERNS, text)


def canonical_branch(text: str) -> str:
    return _first(_BRANCH_PATTERNS, text)


first_branch = canonical_branch


def canonical_degree(text: str) -> Optional[DegreeId]:
    return _DEGREE_GROUPS.get(first_degree(text))


def degrees_equivalent(resume: Optional[DegreeId], jd: Optional[DegreeId]) -> bool:
    if not resume or not jd:
        return False
    if jd.generic:
        return resume.level == jd.level
    return resume.group == jd.group


def is_related_branch(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a == b:
        return True
    return b in RELATED_BRANCHES.get(a, set())


def extract_qualifications(text: str) -> List[str]:
    found: List[str] = []
    remaining = text or ""

    for display, pattern in _DEGREE_PATTERNS:
        if pattern.search(remaining):
            if display not in found:
                found.append(display)
            remaining = pattern.sub(" ", remaining)

    for display, pattern in _BRANCH_PATTERNS:
        if display not in found and pattern.search(remaining):
            found.append(display)
    return found


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
    years = [
        float(x)
        for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)", text)
    ]
    months = [
        float(x) / 12 for x in re.findall(r"(\d+)\s*(?:months|month|mos)\b", text)
    ]
    return round(max(years + months + [0.0]), 1)
