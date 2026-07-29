from __future__ import annotations

from backend.schemas.chatbot import CandidateEvidence


class CopilotResponseFormatter:
    def fallback_answer(
        self,
        message: str,
        candidates: list[CandidateEvidence],
    ) -> str:
        if not candidates:
            return (
                "I could not find a strong candidate match in the current ATS index. "
                "Try adding more role details, required skills, or selecting a job posting."
            )

        lines = [
            "Based on the retrieved ATS evidence, these are the strongest matches:",
            "",
        ]

        for index, candidate in enumerate(candidates[:5], start=1):
            lines.append(
                f"{index}. **{candidate.candidate_name or 'Unknown Candidate'}** "
                f"({round(candidate.final_score * 100)}% RAG score)"
            )
            if candidate.matched_skills:
                lines.append(
                    f"   - Matched skills: {', '.join(candidate.matched_skills[:8])}"
                )
            if candidate.experience_highlights:
                lines.append("   - Experience match: relevant experience section retrieved")
            if candidate.project_highlights:
                lines.append("   - Project match: relevant project evidence retrieved")
            if candidate.relevant_sections:
                sections = ", ".join(
                    section.name
                    for section in candidate.relevant_sections[:4]
                )
                lines.append(f"   - Resume sections used: {sections}")
            if candidate.missing_skills:
                lines.append(
                    f"   - Missing or unconfirmed skills: {', '.join(candidate.missing_skills[:6])}"
                )

        lines.extend(
            [
                "",
                "Shortlist recommendation: prioritize candidates with matched required skills, relevant project or experience evidence, and high recruiter scores. Review the candidate cards for exact resume sections used.",
            ]
        )

        return "\n".join(lines)

    def ensure_recruiter_structure(self, answer: str) -> str:
        if not answer.strip():
            return "I could not generate a response from the available ATS evidence."

        required_terms = [
            "matched",
            "skills",
            "experience",
            "section",
        ]
        lowered = answer.lower()

        if all(term in lowered for term in required_terms):
            return answer.strip()

        return (
            answer.strip()
            + "\n\nEvidence note: candidate cards below show matched skills, relevant experience, resume sections used, and missing or unconfirmed skills from the query."
        )
