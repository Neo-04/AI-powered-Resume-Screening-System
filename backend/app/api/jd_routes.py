from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.schemas.jd import JobDescription
from backend.app.services import jd_service
from backend.app.services.jd_service import JDProcessingError

router = APIRouter(tags=["job-description"])


@router.post("/upload-jd", response_model=JobDescription)
async def upload_jd(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    # Prefer an uploaded file; fall back to pasted text.
    if file is not None and file.filename:
        filename = file.filename
        content_type = file.content_type
        file_bytes = await file.read()
    elif text and text.strip():
        filename = "pasted_jd.txt"
        content_type = "text/plain"
        file_bytes = text.encode("utf-8")
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide a JD file (PDF/TXT) or paste JD text.",
        )

    try:
        return jd_service.process_job_description(
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
        )
    except JDProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/jd/{jd_id}", response_model=JobDescription)
async def get_jd(jd_id: str):
    try:
        return jd_service.get_job_description(jd_id)
    except JDProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
