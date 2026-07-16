from fastapi import APIRouter, HTTPException

from backend.app.schemas.matching import MatchRequest, MatchResult
from backend.app.services import matching_service
from backend.app.services.jd_service import JDProcessingError
from backend.app.services.resume_service import ResumeProcessingError

router = APIRouter(tags=["matching"])


@router.post("/match", response_model=MatchResult)
async def match(payload: MatchRequest):
    try:
        return matching_service.run_match(payload.resume_id, payload.jd_id)
    except (ResumeProcessingError, JDProcessingError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
