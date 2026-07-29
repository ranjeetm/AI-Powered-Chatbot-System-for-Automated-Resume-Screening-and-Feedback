from __future__ import annotations

import asyncio
import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.extraction.skill_extractor import SkillExtractor
from backend.repositories.jd_matching_repository import JDMatchingRepository
from backend.scoring.skill_normalizer import normalize_skill
from backend.schemas.jd_matching import CandidateMatchResult
from backend.services.jd_matching.email_service import EmailJSEmailService
from backend.services.jd_matching.feedback_service import AIMatchFeedbackService


class JDMatchingService:
    def __init__(
        self,
        repository: JDMatchingRepository | None = None,
        feedback_service: AIMatchFeedbackService | None = None,
        email_service: EmailJSEmailService | None = None,
        skill_extractor: SkillExtractor | None = None,
    ):
        self.repository = repository or JDMatchingRepository()
        self.feedback_service = feedback_service or AIMatchFeedbackService()
        self.email_service = email_service or EmailJSEmailService()
        self.skill_extractor = skill_extractor or SkillExtractor()

    async def match_candidates(
        self,
        db: Session,
        *,
        job_description_id: int,
        top_k: int,
        generate_ai_feedback: bool,
        notify_recruiter: bool,
        recruiter_email: str | None,
    ) -> tuple[Any, list[CandidateMatchResult], bool]:
        jd = self.repository.get_job_description(db, job_description_id)

        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")

        rows = self.repository.hybrid_candidate_search(
            db,
            jd_embedding=list(jd.embedding),
            jd_text=jd.description,
            limit=max(top_k * 4, top_k),
        )
        jd_skills = jd.extracted_skills or self.skill_extractor.extract_skills(
            jd.description
        )
        required_experience = self._required_experience_from_jd(
            jd.description,
            jd.inferred_seniority,
        )
        ranked_rows = sorted(
            [
                self._score_row(
                    row,
                    jd_skills,
                    required_experience,
                )
                for row in rows
            ],
            key=lambda item: item["final_score"],
            reverse=True,
        )[:top_k]
        feedback_tasks = [
            self.feedback_service.generate_feedback(
                job_title=jd.title,
                job_description=jd.description,
                candidate=row,
                matched_skills=row["matched_skills"],
                missing_skills=row["missing_skills"],
                final_score=row["final_score"],
            )
            if generate_ai_feedback
            else asyncio.sleep(
                0,
                result=self.feedback_service.fallback_feedback(
                    matched_skills=row["matched_skills"],
                    missing_skills=row["missing_skills"],
                    final_score=row["final_score"],
                ),
            )
            for row in ranked_rows
        ]
        feedback_payloads = await asyncio.gather(*feedback_tasks)
        match_results: list[CandidateMatchResult] = []

        for row, feedback in zip(ranked_rows, feedback_payloads):
            strengths = feedback.get("strengths") or row["matched_skills"]
            result = self.repository.create_match_result(
                db,
                candidate_id=int(row["id"]),
                job_description_id=jd.id,
                semantic_score=row["semantic_score"],
                skill_score=row["skill_score"],
                experience_score=row["experience_score"],
                final_score=row["final_score"],
                strengths=strengths,
                matched_skills=row["matched_skills"],
                missing_skills=row["missing_skills"],
                ai_feedback=feedback,
            )
            match_results.append(
                CandidateMatchResult(
                    match_result_id=result.id,
                    candidate_id=int(row["id"]),
                    candidate_name=row.get("candidate_name"),
                    candidate_email=row.get("email"),
                    category=row.get("category"),
                    experience_years=row.get("experience_years"),
                    semantic_score=round(row["semantic_score"], 4),
                    skill_score=round(row["skill_score"], 4),
                    experience_score=round(row["experience_score"], 4),
                    recruiter_score=round(row["recruiter_score"], 4),
                    final_score=round(row["final_score"], 4),
                    matched_skills=row["matched_skills"],
                    missing_skills=row["missing_skills"],
                    strengths=strengths,
                    ai_feedback=feedback,
                )
            )

        email_sent = False
        if notify_recruiter and recruiter_email:
            email_sent = await self.send_recruiter_email(
                db,
                job_description_id=jd.id,
                match_result_ids=[match.match_result_id for match in match_results],
                recipient_email=recruiter_email,
                email_type="shortlist",
            )

        return jd, match_results, email_sent

    async def send_recruiter_email(
        self,
        db: Session,
        *,
        job_description_id: int,
        match_result_ids: list[int],
        recipient_email: str,
        email_type: str,
    ) -> bool:
        jd = self.repository.get_job_description(db, job_description_id)

        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")

        if match_result_ids:
            rows = self.repository.get_match_results(db, match_result_ids)
        else:
            rows = self.repository.list_match_results_for_jd(db, job_description_id)

        matches = [
            {
                "candidate_name": candidate.candidate_name,
                "final_score": result.final_score,
                "matched_skills": result.matched_skills or [],
                "missing_skills": result.missing_skills or [],
                "ai_feedback": result.ai_feedback or {},
            }
            for result, candidate in rows
        ]
        subject, text, html = self.email_service.build_recruiter_summary(
            job_title=jd.title,
            matches=matches,
            email_type=email_type,
        )

        return await self.email_service.send_email(
            to_email=recipient_email,
            subject=subject,
            text=text,
            html=html,
        )

    def _score_row(
        self,
        row: dict[str, Any],
        jd_skills: list[str],
        required_experience_years: float | None = None,
    ) -> dict[str, Any]:
        candidate_skills = {
            normalize_skill(skill)
            for skill in row.get("skills") or []
            if str(skill).strip()
        }

        candidate_skills.update(
            normalize_skill(skill)
            for skill in self.skill_extractor.extract_skills(
                row.get("resume_text") or row.get("resume_summary") or ""
            )
            if str(skill).strip()
        )
        required_skills = []

        for skill in jd_skills or []:

            normalized = normalize_skill(skill)

            if normalized and normalized not in required_skills:

                required_skills.append(normalized)
        display_skill_map = {
            normalize_skill(skill): str(skill).strip()
            for skill in row.get("skills") or []
            if str(skill).strip()
        }
        matched_skills = [
            display_skill_map.get(skill, skill)
            for skill in required_skills
            if skill in candidate_skills
        ]
        missing_skills = [
            skill
            for skill in required_skills
            if skill not in candidate_skills
        ]
        semantic_score = float(row.get("semantic_similarity") or 0)
        skill_score = len(matched_skills) / len(required_skills) if required_skills else 0.0
        experience_score = self._experience_alignment(
            row.get("experience_years"),
            required_experience_years,
        )
        recruiter_score = float(row.get("recruiter_boost") or 0)
        final_score = (
            semantic_score * 0.45
            + skill_score * 0.30
            + experience_score * 0.15
            + recruiter_score * 0.10
        )

        return {
            **row,
            "semantic_score": semantic_score,
            "skill_score": skill_score,
            "experience_score": experience_score,
            "recruiter_score": recruiter_score,
            "final_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }

    def _experience_alignment(
        self,
        experience_years: int | None,
        required_experience_years: float | None = None,
    ) -> float:
        years = float(experience_years or 0)
        required_years = (
            float(required_experience_years)
            if required_experience_years is not None
            else 5.0
        )

        if required_years <= 0:
            return 1.0

        return min(years / required_years, 1.0)

    def _required_experience_from_jd(
        self,
        jd_text: str,
        seniority: str | None,
    ) -> float:
        text = jd_text.lower()

        range_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            text,
        )

        if range_match:
            return float(range_match.group(1))

        patterns = [
            r"minimum\s+(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            r"at\s+least\s+(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)\s+of\s+experience",
            r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return float(match.group(1))

        if any(term in text for term in ["fresher", "entry level", "entry-level", "graduate", "intern", "internship", "trainee", "junior", "2025 batch", "2026 batch"]):
            return 0.0

        seniority_defaults = {
            "entry": 0.0,
            "mid": 2.0,
            "senior": 5.0,
            "lead": 8.0,
        }

        return seniority_defaults.get(
            str(seniority or "mid").strip().lower(),
            2.0,
        )
