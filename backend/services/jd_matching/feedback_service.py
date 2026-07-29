from __future__ import annotations

import json
from typing import Any

from backend.services.chatbot.openrouter_client import OpenRouterClient


class AIMatchFeedbackService:
    SYSTEM_PROMPT = """
You are an ATS recruiter assistant. Return strict JSON only.
Analyze the candidate against the job description using only provided evidence.
Do not invent skills or experience.

Schema:
{
  "strengths": [],
  "missing_skills": [],
  "fit_summary": "",
  "interview_recommendation": "",
  "recruiter_notes": "",
  "hiring_recommendation": ""
}
""".strip()

    def __init__(
        self,
        llm_client: OpenRouterClient | None = None,
    ):
        self.llm_client = llm_client or OpenRouterClient()

    async def generate_feedback(
        self,
        *,
        job_title: str,
        job_description: str,
        candidate: dict[str, Any],
        matched_skills: list[str],
        missing_skills: list[str],
        final_score: float,
    ) -> dict[str, Any]:
        fallback = self.fallback_feedback(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            final_score=final_score,
        )

        if not self.llm_client.is_configured():
            return fallback

        prompt = f"""
Job Title: {job_title}
Job Description: {job_description[:3500]}

Candidate Name: {candidate.get("candidate_name") or "Unknown"}
Candidate Category: {candidate.get("category") or "Unknown"}
Experience Years: {candidate.get("experience_years") or 0}
Skills: {", ".join(candidate.get("skills") or [])}
Matched Skills: {", ".join(matched_skills)}
Missing Skills: {", ".join(missing_skills)}
Resume Summary: {(candidate.get("resume_summary") or "")[:1200]}
Experience Evidence: {str(candidate.get("experience") or "")[:1600]}
Project Evidence: {str(candidate.get("projects") or "")[:1600]}
Final Match Score: {round(final_score * 100)}%
""".strip()

        try:
            content = await self.llm_client.complete(
                [
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=650,
            )
            parsed = json.loads(
                content.replace("```json", "").replace("```", "").strip()
            )
            return self.normalize_feedback(parsed, fallback)
        except Exception:
            return fallback

    def fallback_feedback(
        self,
        *,
        matched_skills: list[str],
        missing_skills: list[str],
        final_score: float,
    ) -> dict[str, Any]:
        recommendation = (
            "Strong candidate suitable for technical interview."
            if final_score >= 0.75
            else "Potential fit; recruiter should review missing skills before interview."
            if final_score >= 0.55
            else "Weak fit for this JD based on current resume evidence."
        )

        return {
            "strengths": matched_skills[:8],
            "missing_skills": missing_skills[:8],
            "fit_summary": "Candidate fit was generated from semantic similarity, skill overlap, experience alignment, and recruiter score.",
            "interview_recommendation": recommendation,
            "recruiter_notes": "Review the resume evidence and validate critical missing skills during screening.",
            "hiring_recommendation": recommendation,
        }

    def normalize_feedback(
        self,
        payload: dict[str, Any],
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "strengths": self._list(payload.get("strengths")) or fallback["strengths"],
            "missing_skills": self._list(payload.get("missing_skills")) or fallback["missing_skills"],
            "fit_summary": str(payload.get("fit_summary") or fallback["fit_summary"])[:1000],
            "interview_recommendation": str(payload.get("interview_recommendation") or fallback["interview_recommendation"])[:600],
            "recruiter_notes": str(payload.get("recruiter_notes") or fallback["recruiter_notes"])[:1000],
            "hiring_recommendation": str(payload.get("hiring_recommendation") or fallback["hiring_recommendation"])[:600],
        }

    def _list(
        self,
        value: Any,
    ) -> list[str]:
        if not isinstance(value, list):
            return []

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ][:10]
