import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.parser.parser import extract_text_from_pdf
from backend.repositories.jd_matching_repository import JDMatchingRepository
from backend.schemas.jd_matching import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    MatchRunRequest,
    MatchRunResponse,
    RecruiterEmailRequest,
    RecruiterEmailResponse,
)
from backend.services.jd_matching.jd_ingestion_service import JDIngestionService
from backend.services.jd_matching.matching_service import JDMatchingService


router = APIRouter(
    prefix="/jd-matching",
    tags=["jd-matching"],
)

repository = JDMatchingRepository()
ingestion_service = JDIngestionService(repository=repository)
matching_service = JDMatchingService(repository=repository)


@router.post(
    "/job-descriptions",
    response_model=JobDescriptionResponse,
)
async def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await ingestion_service.create_jd(
        db,
        title=payload.title,
        description=payload.description,
        created_by=getattr(current_user, "id", None),
    )


@router.post(
    "/job-descriptions/upload",
    response_model=JobDescriptionResponse,
)
async def upload_job_description(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filename = file.filename or ""

    if not filename.lower().endswith((".txt", ".md", ".pdf")):
        raise HTTPException(
            status_code=400,
            detail="JD upload supports .txt, .md, or .pdf files",
        )

    content = await file.read()

    if filename.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            parsed = extract_text_from_pdf(str(tmp_path))
            description = parsed.get("text", "")
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        description = content.decode("utf-8", errors="ignore")

    if len(description.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Uploaded JD does not contain enough text",
        )

    return await ingestion_service.create_jd(
        db,
        title=title,
        description=description,
        created_by=getattr(current_user, "id", None),
    )


@router.get(
    "/job-descriptions",
    response_model=list[JobDescriptionResponse],
)
def list_job_descriptions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return repository.list_job_descriptions(db)


@router.post(
    "/match",
    response_model=MatchRunResponse,
)
async def match_job_description(
    payload: MatchRunRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    jd, matches, email_sent = await matching_service.match_candidates(
        db,
        job_description_id=payload.job_description_id,
        top_k=payload.top_k,
        generate_ai_feedback=payload.generate_ai_feedback,
        notify_recruiter=payload.notify_recruiter,
        recruiter_email=str(payload.recruiter_email) if payload.recruiter_email else None,
    )

    return MatchRunResponse(
        job_description=jd,
        matches=matches,
        email_sent=email_sent,
    )


@router.post(
    "/email",
    response_model=RecruiterEmailResponse,
)
async def send_recruiter_email(
    payload: RecruiterEmailRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    sent = await matching_service.send_recruiter_email(
        db,
        job_description_id=payload.job_description_id,
        match_result_ids=payload.match_result_ids,
        recipient_email=str(payload.recipient_email),
        email_type=payload.email_type,
    )

    return RecruiterEmailResponse(
        sent=sent,
        message=(
            "Email sent through EmailJS"
            if sent
            else (
                "Email was not sent. Check EMAILJS_SERVICE_ID, "
                "EMAILJS_TEMPLATE_ID, and EMAILJS_PUBLIC_KEY."
            )
        ),
    )
