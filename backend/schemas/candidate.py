from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List, Any


class CandidateResponse(BaseModel):

    id: int

    file_name: Optional[str] = None

    candidate_name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    location: Optional[str] = None

    linkedin_url: Optional[str] = None

    github_url: Optional[str] = None

    category: Optional[str] = None

    skills: Optional[List[Any]] = None

    job_titles: Optional[List[Any]] = None

    degrees: Optional[List[Any]] = None

    specializations: Optional[List[Any]] = None

    certifications: Optional[List[Any]] = None

    education: Optional[List[Any]] = None

    projects: Optional[List[Any]] = None

    experience: Optional[List[Any]] = None

    experience_years: Optional[int] = None

    resume_summary: Optional[str] = None

    resume_text: Optional[str] = None

    resume_file_path: Optional[str] = None

    is_shortlisted: Optional[bool] = None

    shortlist_updated_at: Optional[datetime] = None

    rejection_feedback: Optional[str] = None

    class Config:
        from_attributes = True
