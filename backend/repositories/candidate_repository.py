from datetime import datetime

from sqlalchemy.orm import Session

from sqlalchemy import text

from backend.db.models import CandidateProfile

# --------------------------------
# INSERT CANDIDATE
# --------------------------------


def insert_candidate(db: Session, profile_data: dict, embedding):

    candidate = CandidateProfile(
        # --------------------------------
        # BASIC INFO
        # --------------------------------
        file_name=profile_data.get("file_name"),
        candidate_name=profile_data.get("candidate_name"),
        email=profile_data.get("email"),
        phone=profile_data.get("phone"),
        location=profile_data.get("location"),
        linkedin_url=profile_data.get("linkedin_url"),
        github_url=profile_data.get("github_url"),
        category=profile_data.get("category"),
        # --------------------------------
        # STRUCTURED DATA
        # --------------------------------
        skills=profile_data.get("skills"),
        job_titles=profile_data.get("job_titles"),
        degrees=profile_data.get("degrees"),
        specializations=profile_data.get("specializations"),
        certifications=profile_data.get("certifications"),
        education=profile_data.get("education"),
        projects=profile_data.get("projects"),
        experience=profile_data.get("experience"),
        sections=profile_data.get("sections"),
        # --------------------------------
        # EXPERIENCE
        # --------------------------------
        experience_years=profile_data.get("experience_years"),
        # --------------------------------
        # TEXT STORAGE
        # --------------------------------
        resume_summary=profile_data.get("resume_summary"),
        resume_text=profile_data.get("resume_text"),
        cleaned_text=profile_data.get("cleaned_text"),
        resume_file_path=profile_data.get("resume_file_path"),
        # --------------------------------
        # SCORING
        # --------------------------------
        semantic_score=profile_data.get("semantic_score", 0.0),
        weighted_score=profile_data.get("weighted_score", 0.0),
        recruiter_score=profile_data.get("recruiter_score", 0.0),
        # --------------------------------
        # VECTOR EMBEDDING
        # --------------------------------
        embedding=list(embedding) if embedding is not None else None,
    )

    db.add(candidate)

    db.commit()

    db.refresh(candidate)

    return candidate


# --------------------------------
# GET CANDIDATE BY ID
# --------------------------------


def get_candidate_by_id(db: Session, candidate_id: int):

    return (
        db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
    )


def update_shortlist_status(
    db: Session,
    candidate_id: int,
    *,
    is_shortlisted: bool,
    rejection_feedback: str | None = None,
) -> CandidateProfile | None:

    candidate = get_candidate_by_id(db, candidate_id)

    if not candidate:

        return None

    candidate.is_shortlisted = is_shortlisted
    candidate.shortlist_updated_at = datetime.utcnow()

    if is_shortlisted:

        candidate.rejection_feedback = None

    else:

        candidate.rejection_feedback = rejection_feedback

    db.commit()
    db.refresh(candidate)

    return candidate


# --------------------------------
# GET TOP CANDIDATES
# --------------------------------


def get_top_candidates(db: Session, limit: int = 10):

    return (
        db.query(CandidateProfile)
        .order_by(CandidateProfile.recruiter_score.desc())
        .limit(limit)
        .all()
    )


# --------------------------------
# VECTOR SEARCH
# --------------------------------


def semantic_search(db: Session, query_embedding, limit: int = 5):

    sql = text("""

        SELECT

            id,

            candidate_name,

            semantic_score,

            weighted_score,

            recruiter_score,

            embedding <=> CAST(
                :embedding AS vector
            ) AS distance

        FROM candidate_profiles

        ORDER BY distance

        LIMIT :limit

    """)

    result = db.execute(sql, {"embedding": query_embedding, "limit": limit})

    return result.fetchall()
