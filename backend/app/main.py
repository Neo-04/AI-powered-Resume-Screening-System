from fastapi import FastAPI

from backend.app.api.jd_routes import router as jd_router
from backend.app.api.matching_routes import router as matching_router
from backend.app.api.parse_routes import router as parse_router
from backend.app.api.routes import router

app = FastAPI(title="AI Resume Screening System", version="0.1.0")

app.include_router(router)
app.include_router(jd_router)
app.include_router(parse_router)
app.include_router(matching_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
