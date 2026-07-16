from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field


@dataclass
class Resume:
    """Internal storage model for an uploaded resume (not the API response)."""

    resume_id: str
    filename: str
    text: str
    char_count: int


class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    char_count: int
    text: str


class ParsedResume(BaseModel):
    resume_id: str
    name: str = ""
    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    degree: str = ""
    branch: str = ""
    experience_years: float = 0.0
