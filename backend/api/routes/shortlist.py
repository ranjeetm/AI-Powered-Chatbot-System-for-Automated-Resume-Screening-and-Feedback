from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.schemas.shortlist import (
    FeedbackSuggestionRequest,
    FeedbackSuggestionResponse,
    ShortlistActionRequest,
    ShortlistActionResponse,
    UnshortlistActionRequest,
)
from backend.services.shortlist.shortlist_service import ShortlistService


router = APIRouter(
    tags=["candidate-shortlist"],
)

shortlist_service = ShortlistService()


@router.post(
    "/candidates/{candidate_id}/shortlist",
    response_model=ShortlistActionResponse,
)
async def shortlist_candidate(
    candidate_id: int,
    payload: ShortlistActionRequest = ShortlistActionRequest(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user

    if not shortlist_service.get_candidate(db, candidate_id):

        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    job_title = payload.job_title

    try:

        message, is_shortlisted, email_sent = await shortlist_service.shortlist_candidate(
            db,
            candidate_id,
            job_title=job_title,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return ShortlistActionResponse(
        message=message,
        is_shortlisted=is_shortlisted,
        email_sent=email_sent,
    )


@router.post(
    "/candidates/{candidate_id}/unshortlist",
    response_model=ShortlistActionResponse,
)
async def unshortlist_candidate(
    candidate_id: int,
    payload: UnshortlistActionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user

    if not shortlist_service.get_candidate(db, candidate_id):

        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    try:

        message, is_shortlisted, email_sent = (
            await shortlist_service.unshortlist_candidate(
                db,
                candidate_id,
                feedback=payload.feedback,
                job_title=payload.job_title,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return ShortlistActionResponse(
        message=message,
        is_shortlisted=is_shortlisted,
        email_sent=email_sent,
    )


@router.post(
    "/candidates/{candidate_id}/feedback-suggestion",
    response_model=FeedbackSuggestionResponse,
)
async def suggest_candidate_feedback(
    candidate_id: int,
    payload: FeedbackSuggestionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user

    try:
        suggestion = await shortlist_service.suggest_rejection_feedback(
            db,
            candidate_id,
            job_description_id=payload.job_description_id,
            job_title=payload.job_title,
            job_description=payload.job_description,
        )

    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return FeedbackSuggestionResponse(**suggestion)
