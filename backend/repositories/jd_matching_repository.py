from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db.models import CandidateProfile, JobDescription, MatchResult


def _to_python_float_vector(
    embedding: Any,
) -> list[float]:
    if embedding is None:
        return []

    return [
        float(value)
        for value in list(embedding)
    ]


class JDMatchingRepository:
    def create_job_description(
        self,
        db: Session,
        *,
        title: str,
        description: str,
        extracted_skills: list[str],
        inferred_category: str,
        inferred_seniority: str,
        embedding: list[float],
        created_by: int | None,
    ) -> JobDescription:
        job_description = JobDescription(
            title=title,
            description=description,
            extracted_skills=extracted_skills,
            inferred_category=inferred_category,
            inferred_seniority=inferred_seniority,
            embedding=_to_python_float_vector(embedding),
            created_by=created_by,
        )

        db.add(job_description)
        db.commit()
        db.refresh(job_description)

        return job_description

    def get_job_description(
        self,
        db: Session,
        job_description_id: int,
    ) -> JobDescription | None:
        return (
            db.query(JobDescription)
            .filter(JobDescription.id == job_description_id)
            .first()
        )

    def list_job_descriptions(
        self,
        db: Session,
        limit: int = 50,
    ) -> list[JobDescription]:
        return (
            db.query(JobDescription)
            .order_by(JobDescription.created_at.desc())
            .limit(limit)
            .all()
        )

    def hybrid_candidate_search(
        self,
        db: Session,
        *,
        jd_embedding: list[float],
        jd_text: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        statement = text(
            """
            WITH scored AS (
                SELECT
                    id,
                    candidate_name,
                    email,
                    category,
                    skills,
                    experience,
                    projects,
                    education,
                    sections,
                    resume_summary,
                    resume_text,
                    experience_years,
                    recruiter_score,
                    embedding <=> CAST(:embedding AS vector) AS distance,
                    ts_rank_cd(
                        to_tsvector(
                            'english',
                            COALESCE(candidate_name, '') || ' ' ||
                            COALESCE(category, '') || ' ' ||
                            COALESCE(skills::text, '') || ' ' ||
                            COALESCE(job_titles::text, '') || ' ' ||
                            COALESCE(resume_summary, '') || ' ' ||
                            COALESCE(cleaned_text, resume_text, '')
                        ),
                        plainto_tsquery('english', :jd_text)
                    ) AS keyword_rank
                FROM candidate_profiles
                WHERE embedding IS NOT NULL
            )
            SELECT
                *,
                GREATEST(0, 1 - distance) AS semantic_similarity,
                LEAST(1, keyword_rank * 4.0) AS keyword_score,
                LEAST(1, COALESCE(recruiter_score, 0) / 100.0) AS recruiter_boost
            FROM scored
            ORDER BY
                (
                    GREATEST(0, 1 - distance) * 0.75 +
                    LEAST(1, keyword_rank * 4.0) * 0.15 +
                    LEAST(1, COALESCE(recruiter_score, 0) / 100.0) * 0.10
                ) DESC,
                distance ASC
            LIMIT :limit
            """
        )

        rows = db.execute(
            statement,
            {
                "embedding": _to_python_float_vector(jd_embedding),
                "jd_text": jd_text,
                "limit": limit,
            },
        ).mappings().all()

        return [dict(row) for row in rows]

    def create_match_result(
        self,
        db: Session,
        *,
        candidate_id: int,
        job_description_id: int,
        semantic_score: float,
        skill_score: float,
        experience_score: float,
        final_score: float,
        strengths: list[str],
        matched_skills: list[str],
        missing_skills: list[str],
        ai_feedback: dict[str, Any],
    ) -> MatchResult:
        result = MatchResult(
            candidate_id=candidate_id,
            job_description_id=job_description_id,
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=experience_score,
            final_score=final_score,
            strengths=strengths,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            ai_feedback=ai_feedback,
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return result

    def get_match_results(
        self,
        db: Session,
        match_result_ids: list[int],
    ) -> list[tuple[MatchResult, CandidateProfile]]:
        if not match_result_ids:
            return []

        return (
            db.query(MatchResult, CandidateProfile)
            .join(CandidateProfile, CandidateProfile.id == MatchResult.candidate_id)
            .filter(MatchResult.id.in_(match_result_ids))
            .order_by(MatchResult.final_score.desc())
            .all()
        )

    def list_match_results_for_jd(
        self,
        db: Session,
        job_description_id: int,
        limit: int = 20,
    ) -> list[tuple[MatchResult, CandidateProfile]]:
        return (
            db.query(MatchResult, CandidateProfile)
            .join(CandidateProfile, CandidateProfile.id == MatchResult.candidate_id)
            .filter(MatchResult.job_description_id == job_description_id)
            .order_by(MatchResult.final_score.desc())
            .limit(limit)
            .all()
        )
