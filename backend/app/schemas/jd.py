from typing import List
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    jd_id: str
    filename: str
    char_count: int
    text: str


class ParsedJD(BaseModel):
    jd_id: str
    role: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_qualification: List[str] = Field(default_factory=list)
    experience: str = ""
    keywords: List[str] = Field(default_factory=list)