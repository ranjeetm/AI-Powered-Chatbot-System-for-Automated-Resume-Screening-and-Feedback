from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from backend.schemas.chatbot import (
    CandidateEvidence,
    ChatMessage,
    ChatRetrievalFilters,
)
from backend.services.chatbot.context_builder import RecruiterContextBuilder
from backend.services.chatbot.openrouter_client import OpenRouterClient
from backend.services.chatbot.reranking_service import RecruiterRerankingService
from backend.services.chatbot.response_formatter import CopilotResponseFormatter
from backend.services.chatbot.retrieval_service import ChatRetrievalService


class RecruiterCopilotService:
    SYSTEM_PROMPT = """
You are an enterprise AI Recruiter Copilot embedded in an ATS.

Use only the provided ATS retrieval context. Do not invent candidates, skills,
employment history, education, or resume facts. If evidence is missing, say it
is missing or unconfirmed.

Answer like a senior recruiter assistant:
- Directly answer the recruiter question.
- Explain why each candidate matched.
- Name matched skills, relevant experience, and relevant resume sections.
- Mention missing or unconfirmed skills when useful.
- For comparisons, explain the tradeoffs and why one candidate ranks higher.
- For JD matching, provide shortlist recommendations and risks.
- Keep the response concise, structured, and recruiter-focused.
""".strip()

    def __init__(
        self,
        retrieval_service: ChatRetrievalService | None = None,
        reranking_service: RecruiterRerankingService | None = None,
        context_builder: RecruiterContextBuilder | None = None,
        llm_client: OpenRouterClient | None = None,
        formatter: CopilotResponseFormatter | None = None,
    ):
        self.retrieval_service = retrieval_service or ChatRetrievalService()
        self.reranking_service = reranking_service or RecruiterRerankingService()
        self.context_builder = context_builder or RecruiterContextBuilder()
        self.llm_client = llm_client or OpenRouterClient()
        self.formatter = formatter or CopilotResponseFormatter()

    async def answer(
        self,
        db: Session,
        message: str,
        history: list[ChatMessage],
        top_k: int,
        filters: ChatRetrievalFilters,
    ) -> tuple[str, list[CandidateEvidence], str, str]:
        candidates, context, intent = await self._build_context(
            db,
            message,
            history,
            top_k,
            filters,
        )

        messages = self._messages(context)

        if not self.llm_client.is_configured():
            answer = self.formatter.fallback_answer(message, candidates)
            return answer, candidates, intent, self.llm_client.model

        model_used = self.llm_client.model
        try:
            answer = await self.llm_client.complete(messages)
            model_used = self.llm_client.last_model_used or self.llm_client.model
        except Exception:
            answer = self.formatter.fallback_answer(message, candidates)

        return (
            self.formatter.ensure_recruiter_structure(answer),
            candidates,
            intent,
            model_used,
        )

    async def stream_answer(
        self,
        db: Session,
        message: str,
        history: list[ChatMessage],
        top_k: int,
        filters: ChatRetrievalFilters,
    ) -> AsyncGenerator[str, None]:
        candidates, context, intent = await self._build_context(
            db,
            message,
            history,
            top_k,
            filters,
        )
        metadata = {
            "type": "metadata",
            "candidates": [
                candidate.model_dump()
                for candidate in candidates
            ],
            "diagnostics": {
                "retrieval_count": len(candidates),
                "model": self.llm_client.last_model_used or self.llm_client.model,
                "intent": intent,
                "filters_applied": filters.model_dump(exclude_none=True),
            },
        }

        yield self._sse(metadata)

        messages = self._messages(context)

        if not self.llm_client.is_configured():
            yield self._sse(
                {
                    "type": "token",
                    "content": self.formatter.fallback_answer(message, candidates),
                }
            )
            yield self._sse({"type": "done"})
            return

        try:
            async for token in self.llm_client.stream(messages):
                yield self._sse(
                    {
                        "type": "token",
                        "content": token,
                    }
                )
        except Exception:
            yield self._sse(
                {
                    "type": "token",
                    "content": self.formatter.fallback_answer(message, candidates),
                }
            )

        yield self._sse(
            {
                "type": "done",
                "model": self.llm_client.last_model_used or self.llm_client.model,
            }
        )

    async def _build_context(
        self,
        db: Session,
        message: str,
        history: list[ChatMessage],
        top_k: int,
        filters: ChatRetrievalFilters,
    ) -> tuple[list[CandidateEvidence], str, str]:
        intent = self._detect_intent(message)
        rows, job_context, query_skills = await self.retrieval_service.retrieve(
            db,
            message,
            top_k,
            filters,
        )
        candidates = self.reranking_service.rerank(
            rows,
            message,
            query_skills,
            top_k,
        )
        context = self.context_builder.build(
            query=message,
            intent=intent,
            candidates=candidates,
            job_context=job_context,
            history=history,
        )

        return candidates, context, intent

    def _messages(self, context: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": context,
            },
        ]

    def _detect_intent(self, message: str) -> str:
        lowered = message.lower()

        if any(term in lowered for term in ["compare", "versus", " vs "]):
            return "candidate_comparison"
        if any(term in lowered for term in ["summarize", "summary"]):
            return "resume_summarization"
        if any(term in lowered for term in ["missing", "lacks", "lack", "gap"]):
            return "missing_skill_analysis"
        if any(term in lowered for term in ["jd", "job description", "match this role"]):
            return "jd_matching"
        if any(term in lowered for term in ["why", "ranked higher", "explain"]):
            return "ranking_explanation"
        if any(term in lowered for term in ["shortlist", "recommend"]):
            return "shortlist_recommendation"

        return "semantic_candidate_search"

    def _sse(self, payload: dict) -> str:
        return f"data: {json.dumps(payload, default=str)}\n\n"
