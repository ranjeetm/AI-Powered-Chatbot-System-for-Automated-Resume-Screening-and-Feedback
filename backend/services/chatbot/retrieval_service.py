from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.orm import Session

from backend.embeddings.embedding_engine import EmbeddingEngine
from backend.extraction.skill_extractor import SkillExtractor
from backend.repositories.chatbot_repository import ChatbotRepository
from backend.schemas.chatbot import ChatRetrievalFilters


class ChatRetrievalService:
    def __init__(
        self,
        repository: ChatbotRepository | None = None,
        embedding_engine: EmbeddingEngine | None = None,
        skill_extractor: SkillExtractor | None = None,
    ):
        self.repository = repository or ChatbotRepository()
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.skill_extractor = skill_extractor or SkillExtractor()

    async def embed_query(self, query: str) -> list[float]:
        embedding = await asyncio.to_thread(
            self.embedding_engine.generate_embedding,
            query,
        )

        return embedding.tolist()

    async def retrieve(
        self,
        db: Session,
        query: str,
        top_k: int,
        filters: ChatRetrievalFilters,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None, list[str]]:
        job_context = self.repository.get_job_context(db, filters.job_id)
        retrieval_query = query

        if job_context:
            retrieval_query = (
                f"{query}\n\nJob title: {job_context.get('title')}\n"
                f"Job description: {job_context.get('description')}\n"
                f"Required skills: {', '.join(job_context.get('skills') or [])}"
            )

        extracted_skills = await asyncio.to_thread(
            self.skill_extractor.extract_skills,
            retrieval_query,
        )
        explicit_skills = [
            str(skill).strip().lower()
            for skill in filters.skills or []
            if str(skill).strip()
        ]
        query_skills = sorted(set(extracted_skills + explicit_skills))
        query_embedding = await self.embed_query(retrieval_query)

        rows = self.repository.hybrid_candidate_search(
            db,
            retrieval_query,
            query_embedding,
            max(top_k * 5, 30),
            filters.model_dump(exclude_none=True),
        )

        return rows, job_context, query_skills
