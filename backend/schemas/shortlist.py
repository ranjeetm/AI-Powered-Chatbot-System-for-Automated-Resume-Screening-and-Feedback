from typing import Optional

from pydantic import BaseModel, Field


class ShortlistActionRequest(BaseModel):
    job_title: Optional[str] = None


class UnshortlistActionRequest(BaseModel):
    feedback: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )
    job_title: Optional[str] = None


class ShortlistActionResponse(BaseModel):
    message: str
    is_shortlisted: bool
    email_sent: bool


class FeedbackSuggestionRequest(BaseModel):
    job_description_id: Optional[int] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None


class FeedbackSuggestionResponse(BaseModel):
    feedback: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    final_score: float = 0.0
