from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import JobPosting
from backend.db.session import get_db
from backend.schemas.job import (
    JobPostingCreate,
    JobPostingResponse
)


router = APIRouter()


@router.get(
    "/jobs",
    response_model=list[JobPostingResponse]
)
def list_jobs(
    db: Session = Depends(get_db)
):

    return (
        db.query(JobPosting)
        .order_by(JobPosting.created_at.desc())
        .all()
    )


@router.post(
    "/jobs",
    response_model=JobPostingResponse
)
def create_job(
    payload: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    title = payload.title.strip()
    description = payload.description.strip()

    if not title:

        raise HTTPException(
            status_code=400,
            detail="Job title is required"
        )

    if not description:

        raise HTTPException(
            status_code=400,
            detail="Job description is required"
        )

    job = JobPosting(
        title=title,
        department=(payload.department or "").strip() or None,
        location=(payload.location or "").strip() or None,
        type=(payload.type or "Full-time").strip() or "Full-time",
        description=description,
        skills=[
            str(skill).strip()
            for skill in payload.skills
            if str(skill).strip()
        ]
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job
