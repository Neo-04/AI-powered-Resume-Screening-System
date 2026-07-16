from typing import List, Tuple

from backend.app.utils import embeddings
from backend.app.utils import semantic_config as cfg


def match_skills(
    missing_required: List[str], unmatched_resume: List[str]
) -> List[Tuple[str, str, float]]:
    """Best-first pairing above threshold; each side is used at most once."""
    if not missing_required or not unmatched_resume:
        return []
    required_vecs = embeddings.encode_texts(missing_required)
    resume_vecs = embeddings.encode_texts(unmatched_resume)
    sims = required_vecs @ resume_vecs.T

    candidates = []
    for i in range(len(missing_required)):
        for j in range(len(unmatched_resume)):
            score = float(sims[i][j])
            if score >= cfg.SKILL_SIMILARITY_THRESHOLD:
                candidates.append((score, i, j))
    candidates.sort(key=lambda c: c[0], reverse=True)

    used_jd, used_resume, hits = set(), set(), []
    for score, i, j in candidates:
        if i in used_jd or j in used_resume:
            continue
        used_jd.add(i)
        used_resume.add(j)
        hits.append((missing_required[i], unmatched_resume[j], score))
    return hits


def match_keywords(
    unmatched_keywords: List[str], resume_text: str
) -> List[Tuple[str, float]]:
    if not unmatched_keywords or not resume_text.strip():
        return []
    keyword_vecs = embeddings.encode_texts(unmatched_keywords)
    doc_vec = embeddings.encode_text(resume_text)
    hits = []
    for i, keyword in enumerate(unmatched_keywords):
        score = float(keyword_vecs[i] @ doc_vec)
        if score >= cfg.KEYWORD_SIMILARITY_THRESHOLD:
            hits.append((keyword, score))
    return hits


def qualification_matches(
    resume_qualification_text: str, jd_qualifications: List[str]
) -> Tuple[bool, float]:
    if not resume_qualification_text.strip() or not jd_qualifications:
        return False, 0.0
    import numpy as np

    resume_vec = embeddings.encode_text(resume_qualification_text)
    jd_vecs = embeddings.encode_texts(jd_qualifications)
    score = float(np.max(jd_vecs @ resume_vec))
    return score >= cfg.QUALIFICATION_SIMILARITY_THRESHOLD, score


def experience_matches(
    resume_experience_text: str, jd_experience_text: str
) -> Tuple[bool, float]:
    if not resume_experience_text.strip() or not jd_experience_text.strip():
        return False, 0.0
    resume_vec = embeddings.encode_text(resume_experience_text)
    jd_vec = embeddings.encode_text(jd_experience_text)
    score = float(resume_vec @ jd_vec)
    return score >= cfg.EXPERIENCE_SIMILARITY_THRESHOLD, score
