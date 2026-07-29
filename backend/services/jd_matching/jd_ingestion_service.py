from __future__ import annotations

import asyncio
import re

from sqlalchemy.orm import Session

from backend.embeddings.embedding_engine import EmbeddingEngine
from backend.extraction.skill_extractor import SkillExtractor
from backend.repositories.jd_matching_repository import JDMatchingRepository


class JDIngestionService:
    def __init__(
        self,
        repository: JDMatchingRepository | None = None,
        embedding_engine: EmbeddingEngine | None = None,
        skill_extractor: SkillExtractor | None = None,
    ):
        self.repository = repository or JDMatchingRepository()
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.skill_extractor = skill_extractor or SkillExtractor()

    async def create_jd(
        self,
        db: Session,
        *,
        title: str,
        description: str,
        created_by: int | None,
    ):
        cleaned_title = title.strip()
        cleaned_description = re.sub(r"\s+", " ", description).strip()
        extracted_skills = await asyncio.to_thread(
            self.skill_extractor.extract_skills,
            cleaned_description,
        )
        embedding = await asyncio.to_thread(
            self.embedding_engine.generate_embedding,
            f"{cleaned_title}\n{cleaned_description}",
        )
        inferred_category = self.infer_category(cleaned_title, cleaned_description, extracted_skills)
        inferred_seniority = self.infer_seniority(cleaned_title, cleaned_description)

        return self.repository.create_job_description(
            db,
            title=cleaned_title,
            description=cleaned_description,
            extracted_skills=extracted_skills,
            inferred_category=inferred_category,
            inferred_seniority=inferred_seniority,
            embedding=embedding.tolist(),
            created_by=created_by,
        )

    def infer_category(
        self,
        title: str,
        description: str,
        skills: list[str],
    ) -> str:
        text = f"{title} {description} {' '.join(skills)}".lower()

        categories = [
            ("data_science", ["machine learning", "data science", "nlp", "pandas", "tensorflow", "pytorch"]),
            ("devops", ["docker", "kubernetes", "terraform", "aws", "azure", "gcp", "linux"]),
            ("backend", ["fastapi", "django", "flask", "api", "postgresql", "sql"]),
            ("frontend", ["react", "javascript", "typescript", "html", "css"]),
            ("hr", ["recruitment", "talent acquisition", "employee relations", "onboarding"]),
        ]

        best_category = "general"
        best_score = 0

        for category, keywords in categories:
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_category = category
                best_score = score

        return best_category

    def infer_seniority(
        self,
        title: str,
        description: str,
    ) -> str:
        text = f"{title} {description}".lower()

        if any(term in text for term in ["principal", "staff", "lead", "architect", "8+ years", "10+ years"]):
            return "Lead"

        if any(term in text for term in ["senior", "sr.", "5+ years", "6+ years", "7+ years"]):
            return "Senior"

        if any(term in text for term in ["intern", "trainee", "fresher", "entry level", "0-1 years"]):
            return "Entry"

        return "Mid"
