from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from backend.db.session import get_db

from backend.schemas.candidate import (
    CandidateResponse
)

from backend.repositories.candidate_repository import (
    get_candidate_by_id
)
from fastapi import Depends

from backend.core.security import (
    get_current_user
)

router = APIRouter()


def resolve_resume_path(
    stored_path: str,
    file_name: str | None
):
    candidates = []
    original_path = Path(stored_path).expanduser()

    candidates.append(original_path)

    if not original_path.is_absolute():

        candidates.append(
            Path.cwd() / original_path
        )

    lookup_names = {
        original_path.name,
        file_name or ""
    }

    for lookup_name in lookup_names:

        if not lookup_name:

            continue

        for folder in [
            Path.cwd() / "uploaded_resumes",
            Path.cwd() / "datasets" / "resumes"
        ]:

            if folder.exists():

                candidates.extend(
                    folder.rglob(lookup_name)
                )

    for path in candidates:

        if path.exists() and path.is_file():

            return path.resolve()

    return None


# --------------------------------
# GET CANDIDATE DETAILS
# --------------------------------

@router.get(
    "/candidate/{candidate_id}",
    response_model=CandidateResponse
)

def get_candidate(

    candidate_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user = Depends(
        get_current_user
    )
):

    candidate = get_candidate_by_id(
        db,
        candidate_id
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate

# --------------------------------
# DOWNLOAD RESUME
# --------------------------------

@router.get(
    "/candidate-resume/{candidate_id}"
)

def download_resume(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = get_candidate_by_id(
        db,
        candidate_id
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    if not candidate.resume_file_path:

        raise HTTPException(
            status_code=404,
            detail="Resume file not found"
        )

    resume_path = resolve_resume_path(
        candidate.resume_file_path,
        candidate.file_name
    )

    if resume_path is None:

        raise HTTPException(
            status_code=404,
            detail="Resume file is no longer available on the server"
        )

    return FileResponse(

        path=str(resume_path),

        filename=candidate.file_name or resume_path.name,

        media_type="application/pdf"
    )
