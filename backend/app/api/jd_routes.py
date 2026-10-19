from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.schemas.jd import JobDescription
from backend.app.services import jd_service
from backend.app.services.jd_service import JDProcessingError

router = APIRouter(tags=["job-description"])


@router.post("/upload-jd", response_model=JobDescription)
async def upload_jd(
    file: UploadFile = File(None, description="Upload a JD file (PDF or TXT)"),
    text: str = Form(None, description="Or paste JD text here"),
):
    # Path 1: uploaded file (PDF/TXT) — stored in Supabase Storage
    if file is not None and file.filename:
        filename = file.filename
        content_type = file.content_type
        file_bytes = await file.read()

        try:
            return jd_service.process_jd_file(
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
            )
        except JDProcessingError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc))

    # Path 2: pasted raw text — no file storage
    if text and text.strip():
        try:
            return jd_service.process_jd_text(raw_text=text.strip())
        except JDProcessingError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc))

    raise HTTPException(
        status_code=400,
        detail="Provide a JD file (PDF/TXT) or paste JD text.",
    )


@router.get("/jd/{jd_id}", response_model=JobDescription)
async def get_jd(jd_id: str):
    try:
        return jd_service.get_job_description(jd_id)
    except JDProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
