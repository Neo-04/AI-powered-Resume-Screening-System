from fastapi import APIRouter, HTTPException

from backend.app.schemas.jd import ParsedJD
from backend.app.schemas.resume import ParsedResume
from backend.app.services import jd_parser, resume_parser
from backend.app.services.jd_service import JDProcessingError
from backend.app.services.resume_service import ResumeProcessingError

router = APIRouter(tags=["parsing"])


@router.post("/parse-resume/{resume_id}", response_model=ParsedResume)
async def parse_resume(resume_id: str):
    try:
        return resume_parser.parse_resume(resume_id)
    except ResumeProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/parse-jd/{jd_id}", response_model=ParsedJD)
async def parse_jd(jd_id: str):
    try:
        return jd_parser.parse_jd(jd_id)
    except JDProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))