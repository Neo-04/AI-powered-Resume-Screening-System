from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.resume import ResumeUploadResponse
from backend.app.services import resume_service
from backend.app.services.resume_service import ResumeProcessingError

router = APIRouter(tags=["resume"])


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    file_bytes = await file.read()

    try:
        return resume_service.process_resume(
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
        )
    except ResumeProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
