import re
from typing import Dict, List

_SOFT_SKILL_CUES: Dict[str, List[str]] = {
    "communication": [
        r"\bcommunicat",
        r"\bpresented\b",
        r"\bpresentation",
        r"\bauthored\b",
        r"\bdocument",
        r"\barticulat",
    ],
    "leadership": [
        r"\blead",
        r"\bled\b",
        r"\bmanaged\b",
        r"\bmentore?d?\b",
        r"\bheaded\b",
        r"\bspearheaded\b",
        r"\bcaptain\b",
        r"\bpresident\b",
        r"\bcoordinat",
    ],
    "teamwork": [
        r"\bteams?\b",
        r"\bteamwork\b",
        r"\bcollaborat",
        r"\bcross[- ]functional\b",
    ],
    "collaboration": [r"\bcollaborat", r"\bpartnered\b", r"\bworked with\b"],
    "problem solving": [
        r"\bproblem",
        r"\bsolved\b",
        r"\bresolv",
        r"\bdebug",
        r"\boptimiz",
        r"\btroubleshoot",
    ],
    "analytical thinking": [r"\banaly", r"\bevaluat", r"\bassess", r"\binsights?\b"],
    "critical thinking": [r"\bcritical thinking\b", r"\breasoning\b", r"\banaly"],
    "stakeholder management": [r"\bstakeholder", r"\bclient", r"\bcustomer"],
    "adaptability": [r"\badaptab", r"\badapt\b", r"\bflexible\b", r"\bquick learner\b"],
    "presentation skills": [
        r"\bpresent",
        r"\bpresentation",
        r"\bdemo\b",
        r"\bshowcase",
    ],
    "time management": [
        r"\btime management\b",
        r"\bdeadline",
        r"\bprioritiz",
        r"\bschedul",
    ],
    "business understanding": [r"\bbusiness", r"\bdomain\b", r"\bmarket\b"],
    "customer focus": [r"\bcustomer", r"\bclient", r"\buser[- ]centric\b"],
    "interpersonal skills": [r"\binterpersonal\b", r"\bteam\b", r"\bcollaborat"],
    "attention to detail": [
        r"\battention to detail\b",
        r"\bmeticulous\b",
        r"\baccuracy\b",
        r"\bthorough\b",
    ],
    "creativity": [r"\bcreativ", r"\binnovat", r"\bdesigned\b"],
    "negotiation": [r"\bnegotiat"],
    "mentoring": [r"\bmentor", r"\btaught\b", r"\btrained\b", r"\bguided\b"],
    "decision making": [r"\bdecision", r"\bdecided\b"],
    "organization": [r"\borganiz", r"\barranged\b", r"\bcoordinat"],
    "multitasking": [r"\bmulti[- ]?task", r"\bmultiple projects\b"],
    "ownership": [
        r"\bowned\b",
        r"\bownership\b",
        r"\bresponsible for\b",
        r"\bend[- ]to[- ]end\b",
    ],
}
_SOFT_SKILL_CUES = {
    k: [re.compile(p, re.I) for p in v] for k, v in _SOFT_SKILL_CUES.items()
}


def _normalize(keyword: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", keyword.lower()).strip()


def match_soft_skills(jd_keywords: List[str], resume_text: str) -> List[str]:
    matched = []
    for keyword in jd_keywords:
        key = _normalize(keyword)
        cues = _SOFT_SKILL_CUES.get(key)
        if cues:
            if any(cue.search(resume_text) for cue in cues):
                matched.append(keyword)
        elif re.search(
            r"\b" + re.escape(key) + r"\b", resume_text, re.I
        ):  # unknown keyword, literal
            matched.append(keyword)
    return matched
