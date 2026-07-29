from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class ChatbotRepository:
    def hybrid_candidate_search(
        self,
        db: Session,
        query: str,
        query_embedding: list[float],
        top_n: int,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        conditions = ["embedding IS NOT NULL"]
        params: dict[str, Any] = {
            "query": query,
            "embedding": query_embedding,
            "limit": top_n,
        }

        candidate_ids = filters.get("candidate_ids") or []
        if candidate_ids:
            conditions.append("id = ANY(:candidate_ids)")
            params["candidate_ids"] = candidate_ids

        category = (filters.get("category") or "").strip()
        if category:
            conditions.append("LOWER(COALESCE(category, '')) = LOWER(:category)")
            params["category"] = category

        location = (filters.get("location") or "").strip()
        if location:
            conditions.append("LOWER(COALESCE(location, '')) LIKE LOWER(:location)")
            params["location"] = f"%{location}%"

        min_experience_years = filters.get("min_experience_years")
        if min_experience_years is not None:
            conditions.append("COALESCE(experience_years, 0) >= :min_experience_years")
            params["min_experience_years"] = min_experience_years

        for index, skill in enumerate(filters.get("skills") or []):
            normalized = str(skill).strip()
            if not normalized:
                continue

            key = f"skill_{index}"
            conditions.append(
                "("
                "LOWER(COALESCE(skills::text, '')) LIKE LOWER(:{key}) OR "
                "LOWER(COALESCE(cleaned_text, resume_text, '')) LIKE LOWER(:{key})"
                ")".format(key=key)
            )
            params[key] = f"%{normalized}%"

        where_clause = " AND ".join(conditions)

        statement = text(
            f"""
            WITH scored AS (
                SELECT
                    id,
                    file_name,
                    candidate_name,
                    email,
                    phone,
                    location,
                    linkedin_url,
                    github_url,
                    category,
                    skills,
                    job_titles,
                    degrees,
                    specializations,
                    certifications,
                    education,
                    projects,
                    experience,
                    sections,
                    experience_years,
                    resume_summary,
                    resume_text,
                    cleaned_text,
                    semantic_score,
                    weighted_score,
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
                        plainto_tsquery('english', :query)
                    ) AS keyword_rank
                FROM candidate_profiles
                WHERE {where_clause}
            )
            SELECT
                *,
                GREATEST(0, 1 - distance) AS semantic_similarity,
                LEAST(1, keyword_rank * 4.0) AS keyword_score,
                LEAST(1, COALESCE(recruiter_score, 0) / 100.0) AS recruiter_boost,
                (
                    GREATEST(0, 1 - distance) * 0.62 +
                    LEAST(1, keyword_rank * 4.0) * 0.20 +
                    LEAST(1, COALESCE(recruiter_score, 0) / 100.0) * 0.18
                ) AS retrieval_score
            FROM scored
            ORDER BY retrieval_score DESC, distance ASC
            LIMIT :limit
            """
        )

        rows = db.execute(statement, params).mappings().all()
        return [dict(row) for row in rows]

    def get_job_context(
        self,
        db: Session,
        job_id: int | None,
    ) -> dict[str, Any] | None:
        if not job_id:
            return None

        statement = text(
            """
            SELECT id, title, department, location, type, description, skills
            FROM job_postings
            WHERE id = :job_id
            """
        )

        row = db.execute(statement, {"job_id": job_id}).mappings().first()
        return dict(row) if row else None
