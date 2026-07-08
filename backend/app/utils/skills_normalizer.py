import re

# canonical -> aliases (can be extended with more aliases)
_SKILL_CANONICAL = {
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "deep learning": ["dl"],
    "computer vision": ["cv"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "node.js": ["node", "nodejs", "node js"],
    "react": ["reactjs", "react.js", "react js"],
    "next.js": ["nextjs", "next", "next js"],
    "vue": ["vuejs", "vue.js"],
    "express": ["expressjs", "express.js"],
    "pytorch": ["torch"],
    "tensorflow": ["tensor flow"],
    "scikit-learn": ["scikit learn", "sklearn", "scikitlearn", "scikit"],
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

# separator-insensitive fallback index
_STRIPPED_INDEX = {
    re.sub(r"[\s._/-]+", "", key): value
    for key, value in _ALIAS_TO_CANONICAL.items()
    if len(key) >= 3
}


def canonical_skill(skill: str) -> str:
    key = " ".join(skill.lower().split())
    if key in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[key]
    stripped = re.sub(r"[\s._/-]+", "", key)
    return _STRIPPED_INDEX.get(stripped, stripped)  # fallback keeps unlisted skills comparable