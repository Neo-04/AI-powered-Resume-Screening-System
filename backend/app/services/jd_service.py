import uuid

from backend.app.core.config import settings
from backend.app.database.supabase_client import supabase
from backend.app.schemas.jd import JobDescription
from backend.app.utils.pdf_reader import extract_text_from_pdf
from backend.app.utils.text_cleaner import clean_text


class JDProcessingError(Exception):
    """Raised when a JD cannot be processed. Carries an HTTP status hint."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


_PDF_CONTENT_TYPE = "application/pdf"
_TXT_CONTENT_TYPES = {"text/plain", "application/octet-stream"}


def _extract_text_from_file(filename: str, content_type: str, file_bytes: bytes) -> str:
    name = (filename or "").lower()

    if content_type == _PDF_CONTENT_TYPE or name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    if content_type in _TXT_CONTENT_TYPES or name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")

    raise JDProcessingError("Only PDF or TXT files are supported.", status_code=415)


def _upload_to_storage(filename: str, file_bytes: bytes, content_type: str) -> str:
    """Upload file to Supabase Storage and return the storage path."""
    unique_name = f"jds/{uuid.uuid4().hex}_{filename}"
    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=unique_name,
        file=file_bytes,
        file_options={"content-type": content_type},
    )
    return unique_name


def process_jd_file(
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> JobDescription:
    """Process an uploaded JD file (PDF/TXT) — uploads to storage, extracts text."""
    if not file_bytes:
        raise JDProcessingError("Uploaded file is empty.", status_code=400)

    try:
        raw_text = _extract_text_from_file(filename, content_type, file_bytes)
    except JDProcessingError:
        raise
    except Exception:
        raise JDProcessingError("Could not read the file.", status_code=422)

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise JDProcessingError(
            "No extractable text found in the file.", status_code=422
        )

    # Upload original file to Supabase Storage
    try:
        storage_path = _upload_to_storage(filename, file_bytes, content_type)
    except Exception:
        storage_path = ""

    # Insert into Supabase database
    row = {
        "original_filename": filename,
        "storage_path": storage_path,
        "raw_text": raw_text,
        "extracted_text": cleaned,
    }
    result = supabase.table("job_descriptions").insert(row).execute()
    record = result.data[0]

    return JobDescription(
        jd_id=record["id"],
        filename=filename,
        char_count=len(cleaned),
        text=cleaned,
    )


def process_jd_text(raw_text: str) -> JobDescription:
    """Process pasted JD text — no file upload, stores raw text directly."""
    if not raw_text or not raw_text.strip():
        raise JDProcessingError("JD text cannot be empty.", status_code=400)

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise JDProcessingError(
            "No usable text found in the input.", status_code=422
        )

    # Insert into Supabase database (no storage_path, no file)
    row = {
        "original_filename": "pasted_jd.txt",
        "storage_path": "",
        "raw_text": raw_text,
        "extracted_text": cleaned,
    }
    result = supabase.table("job_descriptions").insert(row).execute()
    record = result.data[0]

    return JobDescription(
        jd_id=record["id"],
        filename="pasted_jd.txt",
        char_count=len(cleaned),
        text=cleaned,
    )


def get_job_description(jd_id: str) -> JobDescription:
    """Fetch a job description from Supabase by its UUID."""
    result = (
        supabase.table("job_descriptions")
        .select("id, original_filename, extracted_text")
        .eq("id", jd_id)
        .execute()
    )
    if not result.data:
        raise JDProcessingError("Job description not found.", status_code=404)

    record = result.data[0]
    text = record["extracted_text"] or ""
    return JobDescription(
        jd_id=record["id"],
        filename=record["original_filename"] or "",
        char_count=len(text),
        text=text,
    )
