import uuid

from backend.app.schemas.resume import Resume, ResumeUploadResponse
from backend.app.utils.pdf_reader import extract_text_from_pdf
from backend.app.utils.text_cleaner import clean_text


class ResumeProcessingError(Exception):
    """Raised when a resume cannot be processed. Carries an HTTP status hint."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


# Simple in-memory store. Swap for a real datastore in a later phase.
_resume_store: dict[str, Resume] = {}


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

    resume_id = uuid.uuid4().hex
    resume = Resume(
        resume_id=resume_id,
        filename=filename,
        text=text,
        char_count=len(text),
    )
    _resume_store[resume_id] = resume

    return ResumeUploadResponse(
        resume_id=resume.resume_id,
        filename=resume.filename,
        char_count=resume.char_count,
        text=resume.text,
    )


def get_resume(resume_id: str):
    record = _resume_store.get(resume_id)
    if record is None:
        raise ResumeProcessingError("Resume not found.", status_code=404)
    return record
