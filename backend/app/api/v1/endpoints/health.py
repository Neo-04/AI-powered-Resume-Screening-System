from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness check used by Docker / orchestration probes."""
    return {"status": "ok"}
