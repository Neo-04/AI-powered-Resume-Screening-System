import re
from typing import Tuple

_FRESHER_CUES = ("fresher", "fresh graduate", "no experience", "entry level", "entry-level")


def _required_years(jd_experience: str) -> Tuple[float, bool]:
    text = (jd_experience or "").lower()
    if not text.strip():
        return 0.0, True
    if any(cue in text for cue in _FRESHER_CUES):
        return 0.0, True
    numbers = re.findall(r"\d+(?:\.\d+)?", text)  # first number is the minimum
    return (float(numbers[0]), False) if numbers else (0.0, True)


def match_experience(candidate_years: float, jd_experience: str) -> bool:
    minimum, freshers_allowed = _required_years(jd_experience)
    if freshers_allowed or minimum <= 0:
        return True
    return candidate_years + 1e-9 >= minimum