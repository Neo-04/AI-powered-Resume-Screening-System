import uuid

from backend.app.schemas.jd import JobDescription
from backend.app.utils.pdf_reader import extract_text_from_pdf
from backend.app.utils.text_cleaner import clean_text


class JDProcessingError(Exception):
    """Raised when a JD cannot be processed. Carries an HTTP status hint."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


# Simple in-memory store. Swap for a real datastore in a later phase.
_jd_store: dict[str, JobDescription] = {}

_PDF_CONTENT_TYPE = "application/pdf"
_TXT_CONTENT_TYPES = {"text/plain", "application/octet-stream"}


def _extract_text(filename: str, content_type: str, file_bytes: bytes) -> str:
    name = (filename or "").lower()

    if content_type == _PDF_CONTENT_TYPE or name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    if content_type in _TXT_CONTENT_TYPES or name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")

    raise JDProcessingError("Only PDF or TXT files are supported.", status_code=415)


def process_job_description(
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> JobDescription:
    if not file_bytes:
        raise JDProcessingError("Uploaded file is empty.", status_code=400)

    try:
        raw_text = _extract_text(filename, content_type, file_bytes)
    except JDProcessingError:
        raise
    except Exception:
        raise JDProcessingError("Could not read the file.", status_code=422)

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise JDProcessingError(
            "No extractable text found in the file.", status_code=422
        )

    jd_id = uuid.uuid4().hex
    record = JobDescription(
        jd_id=jd_id,
        filename=filename,
        char_count=len(cleaned),
        text=cleaned,
    )
    _jd_store[jd_id] = record
    return record


def get_job_description(jd_id: str) -> JobDescription:
    record = _jd_store.get(jd_id)
    if record is None:
        raise JDProcessingError("Job description not found.", status_code=404)
    return record
