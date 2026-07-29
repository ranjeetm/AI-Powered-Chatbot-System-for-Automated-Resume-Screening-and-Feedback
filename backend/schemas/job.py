from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class JobPostingCreate(BaseModel):

    title: str

    department: Optional[str] = None

    location: Optional[str] = None

    type: Optional[str] = "Full-time"

    description: str

    skills: List[str] = []


class JobPostingResponse(BaseModel):

    id: int

    title: str

    department: Optional[str] = None

    location: Optional[str] = None

    type: Optional[str] = None

    description: str

    skills: List[str] = []

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
