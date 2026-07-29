from __future__ import annotations

from typing import Any

from backend.schemas.chatbot import CandidateEvidence, ChatMessage


class RecruiterContextBuilder:
    def build(
        self,
        query: str,
        intent: str,
        candidates: list[CandidateEvidence],
        job_context: dict[str, Any] | None,
        history: list[ChatMessage],
    ) -> str:
        history_block = self._history_block(history)
        job_block = self._job_block(job_context)
        candidate_blocks = "\n\n".join(
            self._candidate_block(index, candidate)
            for index, candidate in enumerate(candidates, start=1)
        )

        if not candidate_blocks:
            candidate_blocks = "No candidates were retrieved from the ATS index."

        return f"""
Recruiter query:
{query}

Detected intent:
{intent}

Recent conversation:
{history_block}

Job context:
{job_block}

Retrieved candidate dossiers:
{candidate_blocks}
""".strip()

    def _history_block(self, history: list[ChatMessage]) -> str:
        if not history:
            return "None"

        recent = history[-6:]
        return "\n".join(
            f"{message.role}: {message.content[:700]}"
            for message in recent
            if message.content
        )

    def _job_block(self, job_context: dict[str, Any] | None) -> str:
        if not job_context:
            return "No explicit job posting selected."

        skills = ", ".join(job_context.get("skills") or [])
        return (
            f"Job ID: {job_context.get('id')}\n"
            f"Title: {job_context.get('title')}\n"
            f"Department: {job_context.get('department') or 'Not specified'}\n"
            f"Location: {job_context.get('location') or 'Not specified'}\n"
            f"Type: {job_context.get('type') or 'Not specified'}\n"
            f"Skills: {skills or 'Not specified'}\n"
            f"Description: {job_context.get('description')}"
        )

    def _candidate_block(
        self,
        index: int,
        candidate: CandidateEvidence,
    ) -> str:
        sections = "\n".join(
            f"- {section.name}: {section.snippet}"
            for section in candidate.relevant_sections
        ) or "- No section-level evidence found."
        reasons = "\n".join(
            f"- {reason}"
            for reason in candidate.matching_reasons
        ) or "- No explicit matching reason available."
        projects = "\n".join(
            f"- {item}"
            for item in candidate.project_highlights
        ) or "- No project highlight retrieved."
        experience = "\n".join(
            f"- {item}"
            for item in candidate.experience_highlights
        ) or "- No experience highlight retrieved."

        return f"""
Candidate {index}
Candidate ID: {candidate.candidate_id}
Candidate Name: {candidate.candidate_name or "Unknown"}
Category: {candidate.category or "Unknown"}
Experience Years: {candidate.experience_years if candidate.experience_years is not None else "Unknown"}
Recruiter Score: {candidate.recruiter_score if candidate.recruiter_score is not None else "Unknown"}
Final RAG Score: {round(candidate.final_score * 100, 1)}%
Semantic Similarity: {round(candidate.semantic_similarity * 100, 1)}%
Keyword Score: {round(candidate.keyword_score * 100, 1)}%
Skills: {", ".join(candidate.skills) or "None extracted"}
Matched Skills: {", ".join(candidate.matched_skills) or "None"}
Missing Skills: {", ".join(candidate.missing_skills) or "None from query"}
Matching Reasons:
{reasons}
Relevant Resume Sections:
{sections}
Experience Highlights:
{experience}
Project Highlights:
{projects}
""".strip()
