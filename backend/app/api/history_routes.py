from fastapi import APIRouter

from backend.app.database.supabase_client import supabase

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/resumes")
async def list_resumes():
    """List all uploaded resumes (most recent first)."""
    result = (
        supabase.table("resumes")
        .select("id, original_filename, storage_path, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/jds")
async def list_job_descriptions():
    """List all uploaded job descriptions (most recent first)."""
    result = (
        supabase.table("job_descriptions")
        .select("id, title, original_filename, storage_path, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/matches")
async def list_match_results():
    """List all match results (most recent first)."""
    result = (
        supabase.table("match_results")
        .select("id, resume_id, jd_id, overall_score, skill_score, experience_score, qualification_score, soft_skill_score, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/resumes/{resume_id}")
async def get_resume_detail(resume_id: str):
    """Get full resume record including extracted text and parsed data."""
    result = (
        supabase.table("resumes")
        .select("*")
        .eq("id", resume_id)
        .execute()
    )
    if not result.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resume not found.")
    return result.data[0]


@router.get("/jds/{jd_id}")
async def get_jd_detail(jd_id: str):
    """Get full job description record including extracted text and parsed data."""
    result = (
        supabase.table("job_descriptions")
        .select("*")
        .eq("id", jd_id)
        .execute()
    )
    if not result.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job description not found.")
    return result.data[0]


@router.get("/matches/{match_id}")
async def get_match_detail(match_id: str):
    """Get full match result record including all scores and result_data."""
    result = (
        supabase.table("match_results")
        .select("*")
        .eq("id", match_id)
        .execute()
    )
    if not result.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Match result not found.")
    return result.data[0]
