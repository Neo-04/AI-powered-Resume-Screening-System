import uuid

from backend.app.database.supabase_client import supabase
from backend.app.core.config import settings
from backend.app.schemas.resume import Resume, ResumeUploadResponse
from backend.app.utils.pdf_reader import extract_text_from_pdf
from backend.app.utils.text_cleaner import clean_text


class ResumeProcessingError(Exception):
    """Raised when a resume cannot be processed. Carries an HTTP status hint."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _upload_to_storage(filename: str, file_bytes: bytes, content_type: str) -> str:
    """Upload file to Supabase Storage and return the storage path."""
    # Create a unique path to avoid collisions
    unique_name = f"resumes/{uuid.uuid4().hex}_{filename}"
    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=unique_name,
        file=file_bytes,
        file_options={"content-type": content_type},
    )
    return unique_name


def process_resume(
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> ResumeUploadResponse:
    if content_type != "application/pdf":
        raise ResumeProcessingError("Only PDF files are supported.", status_code=415)

    if not file_bytes:
        raise ResumeProcessingError("Uploaded file is empty.", status_code=400)

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except Exception:
        raise ResumeProcessingError("Could not read the PDF file.", status_code=422)

    text = clean_text(raw_text)
    if not text:
        raise ResumeProcessingError(
            "No extractable text found in the PDF.", status_code=422
        )

    # Upload original file to Supabase Storage
    try:
        storage_path = _upload_to_storage(filename, file_bytes, content_type)
    except Exception:
        # If storage upload fails, still continue with DB insert (storage_path = "")
        storage_path = ""

    # Insert into Supabase database
    row = {
        "original_filename": filename,
        "storage_path": storage_path,
        "extracted_text": text,
    }
    result = supabase.table("resumes").insert(row).execute()
    record = result.data[0]
    resume_id = record["id"]

    return ResumeUploadResponse(
        resume_id=resume_id,
        filename=filename,
        char_count=len(text),
        text=text,
    )


def get_resume(resume_id: str) -> Resume:
    """Fetch a resume from Supabase by its UUID."""
    result = (
        supabase.table("resumes")
        .select("id, original_filename, extracted_text")
        .eq("id", resume_id)
        .execute()
    )
    if not result.data:
        raise ResumeProcessingError("Resume not found.", status_code=404)

    record = result.data[0]
    text = record["extracted_text"] or ""
    return Resume(
        resume_id=record["id"],
        filename=record["original_filename"],
        text=text,
        char_count=len(text),
    )
