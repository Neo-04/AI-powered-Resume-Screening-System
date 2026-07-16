from functools import lru_cache
from typing import List

from backend.app.utils import semantic_config as cfg

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(cfg.SEMANTIC_MODEL_NAME)
    return _model


def encode_texts(texts: List[str]):
    return get_model().encode(
        list(texts), convert_to_numpy=True, normalize_embeddings=True
    )


@lru_cache(maxsize=8192)
def _encode_cached(text: str):
    return get_model().encode([text], convert_to_numpy=True, normalize_embeddings=True)[
        0
    ]


def encode_text(text: str):
    return _encode_cached(
        text
    )  # cached across requests for stable vocabulary and faster performance
