from sqlalchemy.orm import (
    Session
)

from sqlalchemy import (
    text
)

from .models import (
    CandidateProfile
)


# --------------------------------
# INSERT CANDIDATE
# --------------------------------

def insert_candidate(
    db: Session,
    profile_data: dict,
    embedding
):

    candidate = CandidateProfile(

        # --------------------------------
        # BASIC INFO
        # --------------------------------

        file_name=
            profile_data.get(
                "file_name"
            ),

        candidate_name=
            profile_data.get(
                "candidate_name"
            ),

        email=
            profile_data.get(
                "email"
            ),

        phone=
            profile_data.get(
                "phone"
            ),

        location=
            profile_data.get(
                "location"
            ),

        linkedin_url=
            profile_data.get(
                "linkedin_url"
            ),

        github_url=
            profile_data.get(
                "github_url"
            ),

        category=
            profile_data.get(
                "category"
            ),

        # --------------------------------
        # STRUCTURED DATA
        # --------------------------------

        skills=
            profile_data.get(
                "skills"
            ),

        job_titles=
            profile_data.get(
                "job_titles"
            ),

        degrees=
            profile_data.get(
                "degrees"
            ),

        specializations=
            profile_data.get(
                "specializations"
            ),

        certifications=
            profile_data.get(
                "certifications"
            ),

        education=
            profile_data.get(
                "education"
            ),

        projects=
            profile_data.get(
                "projects"
            ),

        experience=
            profile_data.get(
                "experience"
            ),

        sections=
            profile_data.get(
                "sections"
            ),

        # --------------------------------
        # EXPERIENCE
        # --------------------------------

        experience_years=
            profile_data.get(
                "experience_years"
            ),

        # --------------------------------
        # TEXT STORAGE
        # --------------------------------

        resume_summary=
            profile_data.get(
                "resume_summary"
            ),

        resume_text=
            profile_data.get(
                "resume_text"
            ),

        cleaned_text=
            profile_data.get(
                "cleaned_text"
            ),

        resume_file_path=
            profile_data.get(
                "resume_file_path"
            ),

        # --------------------------------
        # SCORING
        # --------------------------------

        semantic_score=
            profile_data.get(
                "semantic_score",
                0.0
            ),

        weighted_score=
            profile_data.get(
                "weighted_score",
                0.0
            ),

        recruiter_score=
            profile_data.get(
                "recruiter_score",
                0.0
            ),

        # --------------------------------
        # VECTOR EMBEDDING
        # --------------------------------

        embedding=

            list(embedding)

            if embedding is not None

            else None
    )

    db.add(candidate)

    db.commit()

    db.refresh(candidate)

    return candidate


# --------------------------------
# VECTOR SEARCH
# --------------------------------

def semantic_search(
    db,
    query_embedding,
    limit=5
):

    sql = text("""

        SELECT

            id,

            candidate_name,

            semantic_score,

            weighted_score,

            embedding <=> CAST(
                :embedding AS vector
            ) AS distance

        FROM candidate_profiles

        ORDER BY distance

        LIMIT :limit

    """)

    result = db.execute(

        sql,

        {

            "embedding":
                query_embedding,

            "limit":
                limit
        }
    )

    return result.fetchall()
