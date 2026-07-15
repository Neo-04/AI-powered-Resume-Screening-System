import re

# canonical -> interchangeable aliases only
_SKILL_CANONICAL = {
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "deep learning": ["dl"],
    "computer vision": ["cv"],
    "javascript": ["js", "ecmascript"],
    "typescript": ["ts"],
    "node.js": ["node", "nodejs", "node js"],
    "react": ["reactjs", "react.js", "react js"],
    "next.js": ["nextjs", "next js"],
    "vue": ["vuejs", "vue.js"],
    "express": ["expressjs", "express.js"],
    "pytorch": ["torch"],
    "tensorflow": ["tensor flow"],
    "scikit-learn": ["scikit learn", "sklearn", "scikitlearn"],
    "c++": ["c plus plus", "cpp", "cplusplus"],
    "c#": ["c sharp", "csharp"],
    ".net": ["dotnet", "dot net"],
    "postgresql": ["postgres", "psql"],
    "mysql": ["my sql"],
    "microsoft sql server": ["ms sql", "mssql", "sql server", "microsoft sql"],
    "mongodb": ["mongo"],
    "kubernetes": ["k8s"],
    "amazon web services": ["aws"],
    "google cloud platform": ["gcp", "google cloud"],
    "microsoft azure": ["azure"],
    "github actions": ["gh actions", "github ci"],
    "ci/cd": ["cicd", "ci cd"],
    "rest": ["rest api", "restful", "restful api"],
    "graphql": ["graph ql"],
    "power bi": ["powerbi"],
    "html": ["html5"],
    "css": ["css3"],
}

_ALIAS_TO_CANONICAL = {}
for _canonical, _aliases in _SKILL_CANONICAL.items():
    _ALIAS_TO_CANONICAL[_canonical] = _canonical
    for _alias in _aliases:
        _ALIAS_TO_CANONICAL[_alias] = _canonical

_STRIPPED_INDEX = {
    re.sub(r"[\s._/-]+", "", key): value
    for key, value in _ALIAS_TO_CANONICAL.items()
    if len(key) >= 3
}

# Neighbouring but distinct technologies. Members stay separate canonical
# skills; membership only makes them related, never interchangeable.
_RELATED_SKILL_GROUPS = [
    {"javascript", "typescript"},
    {"react", "angular", "vue", "next.js"},
    {"node.js", "express"},
    {"flask", "django", "fastapi"},
    {"postgresql", "mysql", "microsoft sql server", "sql"},
    {"mongodb", "cassandra", "dynamodb"},
    {"docker", "kubernetes"},
    {"machine learning", "deep learning", "artificial intelligence",
     "natural language processing", "computer vision"},
    {"tensorflow", "pytorch", "keras", "scikit-learn"},
    {"pandas", "numpy"},
    {"amazon web services", "microsoft azure", "google cloud platform"},
    {"rest", "graphql"},
    {"java", "kotlin"},
    {"c++", "c"},
    {"jenkins", "github actions", "ci/cd"},
    {"tableau", "power bi"},
    {"spark", "hadoop", "kafka"},
]

RELATED_SKILLS = {}
for _group in _RELATED_SKILL_GROUPS:
    for _skill in _group:
        RELATED_SKILLS.setdefault(_skill, set()).update(_group - {_skill})


def canonical_skill(skill: str) -> str:
    key = " ".join(skill.lower().split())
    if key in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[key]
    stripped = re.sub(r"[\s._/-]+", "", key)
    return _STRIPPED_INDEX.get(stripped, stripped)


def are_related_skills(a: str, b: str) -> bool:
    """True for neighbouring technologies; identical skills are not 'related'."""
    left, right = canonical_skill(a), canonical_skill(b)
    if not left or not right or left == right:
        return False
    return right in RELATED_SKILLS.get(left, set())