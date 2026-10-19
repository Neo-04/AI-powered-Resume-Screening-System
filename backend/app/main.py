import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.jd_routes import router as jd_router
from backend.app.api.matching_routes import router as matching_router
from backend.app.api.parse_routes import router as parse_router
from backend.app.api.routes import router
from backend.app.api.history_routes import router as history_router

app = FastAPI(title="AI Resume Screening System", version="0.1.0")

# CORS — set ALLOWED_ORIGINS in Render env vars to your Vercel URL(s)
# e.g. "https://your-app.vercel.app,https://your-app-git-main.vercel.app"
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(jd_router)
app.include_router(parse_router)
app.include_router(matching_router)
app.include_router(history_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
