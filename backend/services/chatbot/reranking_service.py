from __future__ import annotations

import re
from typing import Any

from backend.schemas.chatbot import CandidateEvidence, RelevantSection


class RecruiterRerankingService:
    SECTION_ALIASES = {
        "skills": "Skills",
        "technical_skills": "Skills",
        "projects": "Projects",
        "experience": "Experience",
        "work_experience": "Experience",
        "education": "Education",
        "certifications": "Certifications",
        "summary": "Summary",
    }

    def rerank(
        self,
        rows: list[dict[str, Any]],
        query: str,
        query_skills: list[str],
        top_k: int,
    ) -> list[CandidateEvidence]:
        tokens = self._query_terms(query)
        candidates = [
            self._build_evidence(row, tokens, query_skills)
            for row in rows
        ]

        candidates.sort(
            key=lambda candidate: (
                candidate.final_score,
                candidate.recruiter_score or 0,
                candidate.semantic_similarity,
            ),
            reverse=True,
        )

        return candidates[:top_k]

    def _build_evidence(
        self,
        row: dict[str, Any],
        tokens: set[str],
        query_skills: list[str],
    ) -> CandidateEvidence:
        skills = self._strings(row.get("skills"))
        normalized_skills = {skill.lower(): skill for skill in skills}
        matched_skills = [
            normalized_skills[skill]
            for skill in query_skills
            if skill in normalized_skills
        ]
        missing_skills = [
            skill
            for skill in query_skills
            if skill not in normalized_skills
        ]

        relevant_sections = self._relevant_sections(
            row,
            tokens,
            set(query_skills),
        )
        project_highlights = self._highlights(
            row.get("projects"),
            tokens,
            set(query_skills),
            limit=3,
        )
        experience_highlights = self._highlights(
            row.get("experience"),
            tokens,
            set(query_skills),
            limit=3,
        )

        semantic_similarity = float(row.get("semantic_similarity") or 0)
        keyword_score = float(row.get("keyword_score") or 0)
        recruiter_boost = float(row.get("recruiter_boost") or 0)
        skill_score = (
            len(matched_skills) / len(query_skills)
            if query_skills
            else 0.0
        )
        section_score = min(len(relevant_sections) / 4, 1.0)
        experience_score = self._experience_score(row.get("experience_years"))

        final_score = (
            semantic_similarity * 0.42
            + keyword_score * 0.16
            + recruiter_boost * 0.14
            + skill_score * 0.18
            + section_score * 0.06
            + experience_score * 0.04
        )

        reasons = self._matching_reasons(
            matched_skills,
            experience_highlights,
            project_highlights,
            relevant_sections,
            row,
        )

        return CandidateEvidence(
            candidate_id=int(row["id"]),
            candidate_name=row.get("candidate_name"),
            category=row.get("category"),
            skills=skills[:24],
            matched_skills=matched_skills[:16],
            missing_skills=missing_skills[:16],
            experience_years=row.get("experience_years"),
            recruiter_score=row.get("recruiter_score"),
            semantic_similarity=round(semantic_similarity, 4),
            keyword_score=round(keyword_score, 4),
            hybrid_score=round(float(row.get("retrieval_score") or 0), 4),
            final_score=round(final_score, 4),
            matching_reasons=reasons[:6],
            relevant_sections=relevant_sections[:5],
            project_highlights=project_highlights,
            experience_highlights=experience_highlights,
        )

    def _query_terms(self, query: str) -> set[str]:
        return {
            term
            for term in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", query.lower())
            if term not in {"with", "from", "that", "this", "have", "has", "who"}
        }

    def _strings(self, value: Any) -> list[str]:
        if not value:
            return []

        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str):
                    result.append(item.strip())
                elif isinstance(item, dict):
                    result.extend(
                        str(inner).strip()
                        for inner in item.values()
                        if isinstance(inner, str)
                    )
            return [item for item in result if item]

        if isinstance(value, str):
            return [value.strip()] if value.strip() else []

        return []

    def _flatten_text(self, value: Any) -> str:
        if not value:
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, list):
            return " ".join(self._flatten_text(item) for item in value)

        if isinstance(value, dict):
            return " ".join(self._flatten_text(item) for item in value.values())

        return str(value)

    def _snippet(self, text: str, tokens: set[str]) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= 280:
            return compact

        lower = compact.lower()
        positions = [
            lower.find(token)
            for token in tokens
            if token and lower.find(token) >= 0
        ]
        start = max(min(positions) - 90, 0) if positions else 0
        snippet = compact[start:start + 280].strip()

        if start > 0:
            snippet = f"...{snippet}"
        if start + 280 < len(compact):
            snippet = f"{snippet}..."

        return snippet

    def _matches(self, text: str, tokens: set[str], skills: set[str]) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in tokens | skills)

    def _relevant_sections(
        self,
        row: dict[str, Any],
        tokens: set[str],
        skills: set[str],
    ) -> list[RelevantSection]:
        sections = row.get("sections") or {}
        relevant: list[RelevantSection] = []

        if isinstance(sections, dict):
            for key, value in sections.items():
                text = self._flatten_text(value)
                if text and self._matches(text, tokens, skills):
                    relevant.append(
                        RelevantSection(
                            name=self.SECTION_ALIASES.get(str(key), str(key).title()),
                            snippet=self._snippet(text, tokens | skills),
                            full_text=self._full_text(text),
                        )
                    )

        fallback_fields = [
            ("Summary", row.get("resume_summary")),
            ("Experience", row.get("experience")),
            ("Projects", row.get("projects")),
            ("Education", row.get("education")),
        ]

        seen = {section.name for section in relevant}
        for name, value in fallback_fields:
            text = self._flatten_text(value)
            if name not in seen and text and self._matches(text, tokens, skills):
                relevant.append(
                    RelevantSection(
                        name=name,
                        snippet=self._snippet(text, tokens | skills),
                        full_text=self._full_text(text),
                    )
                )

        return relevant

    def _full_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()[:4000]

    def _highlights(
        self,
        value: Any,
        tokens: set[str],
        skills: set[str],
        limit: int,
    ) -> list[str]:
        if not value:
            return []

        items = value if isinstance(value, list) else [value]
        highlights = []

        for item in items:
            text = self._flatten_text(item)
            if text and self._matches(text, tokens, skills):
                highlights.append(self._snippet(text, tokens | skills))

            if len(highlights) >= limit:
                break

        return highlights

    def _experience_score(self, value: Any) -> float:
        try:
            years = float(value or 0)
        except (TypeError, ValueError):
            years = 0

        return min(years / 5, 1.0)

    def _matching_reasons(
        self,
        matched_skills: list[str],
        experience_highlights: list[str],
        project_highlights: list[str],
        relevant_sections: list[RelevantSection],
        row: dict[str, Any],
    ) -> list[str]:
        reasons = []

        if matched_skills:
            reasons.append(
                "Matched required skills: " + ", ".join(matched_skills[:8])
            )

        if row.get("experience_years"):
            reasons.append(
                f"Shows {row.get('experience_years')} years of extracted experience."
            )

        if experience_highlights:
            reasons.append("Relevant experience section supports the query.")

        if project_highlights:
            reasons.append("Project history contains query-aligned work.")

        if relevant_sections:
            sections = ", ".join(section.name for section in relevant_sections[:4])
            reasons.append(f"Evidence found in resume sections: {sections}.")

        if row.get("recruiter_score"):
            reasons.append(
                f"Existing recruiter score contributes a {round(float(row.get('recruiter_score')), 1)} boost."
            )

        return reasons
