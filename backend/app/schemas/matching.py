from typing import List

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    resume_id: str
    jd_id: str


class MatchResult(BaseModel):
    match_score: int
    skill_score: int = 0
    experience_score: int = 0
    qualification_score: int = 0
    soft_skill_score: int = 0
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    additional_skills: List[str] = Field(default_factory=list)
    qualification_match: bool = False
    matching_reason: str = ""
    experience_match: bool = False
    matched_keywords: List[str] = Field(default_factory=list)
    recommendation: str = ""
