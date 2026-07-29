import os
import tempfile
import logging
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    BackgroundTasks,
)
from sqlalchemy.orm import Session

from backend.schemas.upload import (
    CandidateApplyResponse,
    UploadResumeResponse
)

from backend.core.security import (
    get_current_user
)
from backend.db.models import JobPosting
from backend.db.session import get_db

from backend.tasks.resume_tasks import (
    process_resume_task,
    process_resume_background,
)


logger = logging.getLogger(__name__)


router = APIRouter()


UPLOAD_DIR = Path(
    os.getenv(
        "RESUME_UPLOAD_DIR",
        str(
            Path(tempfile.gettempdir())
            / "resume_project_uploads"
        )
    )
).resolve()

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def validate_pdf_filename(
    uploaded_file: UploadFile
):

    filename = os.path.basename(
        uploaded_file.filename or ""
    )

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported"
        )

    return filename


async def save_upload_file(
    file: UploadFile,
    filename: str,
    prefix: str | None = None
):

    stored_filename = (
        f"{prefix}_{filename}"
        if prefix
        else filename
    )

    file_path = UPLOAD_DIR / stored_filename

    with file_path.open(
        "wb"
    ) as f:

        content = await file.read()

        f.write(content)

    return file_path


@router.post(
    "/upload-resume",
    response_model=UploadResumeResponse
)

async def upload_resume(

    file: UploadFile = File(...),

    background_tasks: BackgroundTasks = BackgroundTasks(),

    current_user = Depends(
        get_current_user
    )
):

    # --------------------------------
    # VALIDATE FILE
    # --------------------------------

    filename = validate_pdf_filename(
        file
    )

    # --------------------------------
    # SAVE FILE
    # --------------------------------

    file_path = await save_upload_file(
        file,
        filename
    )

    # --------------------------------
    # QUEUE RESUME PROCESSING
    # --------------------------------

    try:

        background_tasks.add_task(
            process_resume_background,
            str(file_path),
            "uploaded"
        )

    except Exception:

        logger.exception(
            "Failed to enqueue resume processing file_name=%s file_path=%s",
            filename,
            file_path
        )

        raise HTTPException(
            status_code=503,
            detail="Resume saved, but processing queue is unavailable"
        )

    # --------------------------------
    # RESPONSE
    # --------------------------------

    return UploadResumeResponse(
        message="Resume queued for processing",
        file_name=filename
    )


@router.post(
    "/candidate-apply",
    response_model=CandidateApplyResponse
)
async def candidate_apply(

    name: str = Form(...),

    email: str = Form(...),

    job_id: int = Form(...),

    file: UploadFile = File(...),

    background_tasks: BackgroundTasks = BackgroundTasks(),

    db: Session = Depends(
        get_db
    )
):

    candidate_name = name.strip()

    candidate_email = email.strip()

    if not candidate_name:

        raise HTTPException(
            status_code=400,
            detail="Candidate name is required"
        )

    if not candidate_email:

        raise HTTPException(
            status_code=400,
            detail="Candidate email is required"
        )

    job = (
        db.query(JobPosting)
        .filter(JobPosting.id == job_id)
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job posting not found"
        )

    filename = validate_pdf_filename(
        file
    )

    file_path = await save_upload_file(
        file,
        filename,
        prefix=f"candidate_{uuid.uuid4().hex}"
    )

    try:

        background_tasks.add_task(
            process_resume_background,
            file_path=str(file_path),
            category="candidate_application",
            metadata_overrides={
                "candidate_name": candidate_name,
                "email": candidate_email,
                "category": job.title,
            }
        )

    except Exception:

        logger.exception(
            "Failed to enqueue candidate application file_name=%s file_path=%s",
            filename,
            file_path
        )

        raise HTTPException(
            status_code=503,
            detail="Resume saved, but processing queue is unavailable"
        )

    return CandidateApplyResponse(
        message="Application submitted for resume processing",
        file_name=filename,
        candidate_name=candidate_name,
        email=candidate_email
    )
