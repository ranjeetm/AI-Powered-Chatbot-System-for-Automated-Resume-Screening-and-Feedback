from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=20)


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    extracted_skills: list[str] = Field(default_factory=list)
    inferred_category: Optional[str] = None
    inferred_seniority: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[Any] = None


class MatchRunRequest(BaseModel):
    job_description_id: int
    top_k: int = Field(default=10, ge=1, le=50)
    generate_ai_feedback: bool = True
    notify_recruiter: bool = False
    recruiter_email: Optional[EmailStr] = None


class CandidateMatchResult(BaseModel):
    match_result_id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    category: Optional[str] = None
    experience_years: Optional[int] = None
    semantic_score: float
    skill_score: float
    experience_score: float
    recruiter_score: float
    final_score: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    ai_feedback: dict[str, Any] = Field(default_factory=dict)


class MatchRunResponse(BaseModel):
    job_description: JobDescriptionResponse
    matches: list[CandidateMatchResult] = Field(default_factory=list)
    email_sent: bool = False


class RecruiterEmailRequest(BaseModel):
    job_description_id: int
    match_result_ids: list[int] = Field(default_factory=list)
    recipient_email: EmailStr
    email_type: str = Field(default="shortlist", pattern="^(shortlist|interview|feedback)$")


class RecruiterEmailResponse(BaseModel):
    sent: bool
    message: str
