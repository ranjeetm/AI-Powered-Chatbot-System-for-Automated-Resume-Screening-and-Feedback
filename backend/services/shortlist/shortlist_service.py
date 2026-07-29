from __future__ import annotations

from sqlalchemy.orm import Session

from backend.repositories.candidate_repository import (
    get_candidate_by_id,
    update_shortlist_status,
)
from backend.repositories.jd_matching_repository import JDMatchingRepository
from backend.scoring.skill_normalizer import normalize_skill
from backend.extraction.skill_extractor import SkillExtractor
from backend.services.jd_matching.feedback_service import AIMatchFeedbackService
from backend.services.shortlist.email_service import ShortlistEmailService


class ShortlistService:
    def __init__(
        self,
        email_service: ShortlistEmailService | None = None,
        jd_repository: JDMatchingRepository | None = None,
        skill_extractor: SkillExtractor | None = None,
        feedback_service: AIMatchFeedbackService | None = None,
    ):
        self.email_service = email_service or ShortlistEmailService()
        self.jd_repository = jd_repository or JDMatchingRepository()
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.feedback_service = feedback_service or AIMatchFeedbackService()

    async def shortlist_candidate(
        self,
        db: Session,
        candidate_id: int,
        *,
        job_title: str | None = None,
    ) -> tuple[str, bool, bool]:
        candidate = update_shortlist_status(
            db,
            candidate_id,
            is_shortlisted=True,
        )

        if not candidate:

            raise ValueError("Candidate not found")

        email_sent = False
        message = "Candidate shortlisted."

        if not candidate.email:

            message = (
                "Candidate shortlisted. No email on file; notification was not sent."
            )

        elif not self.email_service.is_configured():

            message = (
                "Candidate shortlisted. Email service is not configured; "
                "notification was not sent."
            )

        else:

            email_sent = await self.email_service.send_shortlisted_email(
                to_email=candidate.email,
                candidate_name=candidate.candidate_name or "Candidate",
                job_title=job_title,
            )

            if email_sent:

                message = "Candidate shortlisted and notification email sent."

            else:

                error = self.email_service.last_error
                message = (
                    "Candidate shortlisted. Email delivery failed; "
                    + (
                        error
                        if error
                        else (
                            "check EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, "
                            "and EMAILJS_PUBLIC_KEY."
                        )
                    )
                )

        return message, True, email_sent

    async def unshortlist_candidate(
        self,
        db: Session,
        candidate_id: int,
        *,
        feedback: str,
        job_title: str | None = None,
    ) -> tuple[str, bool, bool]:
        candidate = update_shortlist_status(
            db,
            candidate_id,
            is_shortlisted=False,
            rejection_feedback=feedback,
        )

        if not candidate:

            raise ValueError("Candidate not found")

        email_sent = False
        message = "Candidate removed from shortlist."

        if not candidate.email:

            message = (
                "Candidate removed from shortlist. No email on file; "
                "notification was not sent."
            )

        elif not self.email_service.is_configured():

            message = (
                "Candidate removed from shortlist. Email service is not configured; "
                "notification was not sent."
            )

        else:

            email_sent = await self.email_service.send_unshortlisted_email(
                to_email=candidate.email,
                candidate_name=candidate.candidate_name or "Candidate",
                feedback=feedback,
                job_title=job_title,
            )

            if email_sent:

                message = (
                    "Candidate removed from shortlist and notification email sent."
                )

            else:

                error = self.email_service.last_error
                message = (
                    "Candidate removed from shortlist. Email delivery failed; "
                    + (
                        error
                        if error
                        else (
                            "check EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, "
                            "and EMAILJS_PUBLIC_KEY."
                        )
                    )
                )

        return message, False, email_sent

    def get_candidate(self, db: Session, candidate_id: int):
        return get_candidate_by_id(db, candidate_id)

    async def suggest_rejection_feedback(
        self,
        db: Session,
        candidate_id: int,
        *,
        job_description_id: int | None = None,
        job_title: str | None = None,
        job_description: str | None = None,
    ) -> dict:
        candidate = get_candidate_by_id(db, candidate_id)

        if not candidate:
            raise ValueError("Candidate not found")

        jd = None

        if job_description_id:
            jd = self.jd_repository.get_job_description(db, job_description_id)

            if not jd:
                raise ValueError("Job description not found")

            job_title = job_title or jd.title
            job_description = job_description or jd.description

        if not job_description or len(job_description.strip()) < 20:
            raise ValueError("A job description is required to suggest feedback")

        required_skills = self._unique_normalized_skills(
            self.skill_extractor.extract_skills(job_description)
        )
        candidate_skill_map = self._candidate_skill_map(candidate)
        matched_skills = [
            candidate_skill_map.get(skill, skill)
            for skill in required_skills
            if skill in candidate_skill_map
        ]
        missing_skills = [
            skill
            for skill in required_skills
            if skill not in candidate_skill_map
        ][:8]
        final_score = (
            len(matched_skills) / len(required_skills)
            if required_skills
            else 0.0
        )
        candidate_payload = {
            "candidate_name": candidate.candidate_name,
            "category": candidate.category,
            "experience_years": candidate.experience_years,
            "skills": candidate.skills or [],
            "resume_summary": candidate.resume_summary,
            "experience": candidate.experience,
            "projects": candidate.projects,
        }
        ai_feedback = await self.feedback_service.generate_feedback(
            job_title=job_title or "the role",
            job_description=job_description,
            candidate=candidate_payload,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            final_score=final_score,
        )

        return {
            "feedback": self._candidate_facing_feedback(
                job_title=job_title,
                matched_skills=ai_feedback.get("strengths") or matched_skills,
                missing_skills=ai_feedback.get("missing_skills") or missing_skills,
                fit_summary=ai_feedback.get("fit_summary"),
            ),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "final_score": round(final_score, 4),
        }

    def _candidate_skill_map(self, candidate) -> dict[str, str]:
        display_map = {
            normalize_skill(skill): str(skill).strip()
            for skill in candidate.skills or []
            if str(skill).strip()
        }
        resume_text = " ".join(
            value
            for value in [
                candidate.resume_summary or "",
                candidate.resume_text or "",
            ]
            if value
        )

        for skill in self.skill_extractor.extract_skills(resume_text):
            normalized = normalize_skill(skill)

            if normalized:
                display_map.setdefault(normalized, str(skill).strip())

        return display_map

    def _unique_normalized_skills(self, skills: list[str]) -> list[str]:
        normalized_skills = []

        for skill in skills:
            normalized = normalize_skill(skill)

            if normalized and normalized not in normalized_skills:
                normalized_skills.append(normalized)

        return normalized_skills

    def _candidate_facing_feedback(
        self,
        *,
        job_title: str | None,
        matched_skills: list[str],
        missing_skills: list[str],
        fit_summary: str | None,
    ) -> str:
        role_line = f" for the {job_title} role" if job_title else ""
        strengths = ", ".join(matched_skills[:4])
        gaps = ", ".join(missing_skills[:5])
        sentences = [
            (
                f"Thank you for applying{role_line}. After reviewing your resume "
                "against the current job requirements, we are moving forward with "
                "candidates whose experience more closely matches the role at this time."
            )
        ]

        if strengths:
            sentences.append(
                f"Your profile showed relevant strengths in {strengths}."
            )

        if gaps:
            sentences.append(
                "The main areas where we needed stronger evidence were "
                f"{gaps}."
            )
        elif fit_summary:
            sentences.append(str(fit_summary)[:400])

        sentences.append(
            "We appreciate your interest and encourage you to apply again for roles "
            "that align closely with your background."
        )

        return " ".join(sentences)
