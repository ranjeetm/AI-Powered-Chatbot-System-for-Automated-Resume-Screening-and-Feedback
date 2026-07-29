import os
import logging

from backend.embeddings.embedding_engine import EmbeddingEngine

from backend.db.database import SessionLocal

from backend.db.crud import insert_candidate

from backend.parser.parser import extract_text_from_pdf

from backend.extraction.structured_parser import StructuredResumeParser

from backend.services.llm_enrichment import enrich_resume

logger = logging.getLogger(__name__)


class ResumeIngestionService:

    def __init__(self):

        # --------------------------------
        # EMBEDDING ENGINE
        # --------------------------------

        self.embedding_engine = EmbeddingEngine()

        # --------------------------------
        # STRUCTURED PARSER
        # --------------------------------

        self.parser = StructuredResumeParser()

        # --------------------------------
        # DATABASE SESSION
        # --------------------------------

        self.db = SessionLocal()

    def close(self):

        self.db.close()

    # --------------------------------
    # PROCESS RESUME
    # --------------------------------

    def process_resume(self, file_path, category="unknown", metadata_overrides=None):

        file_name = os.path.basename(file_path)

        logger.info(
            "Starting resume ingestion file_name=%s category=%s file_path=%s",
            file_name,
            category,
            file_path,
        )

        try:

            # --------------------------------
            # PDF TEXT EXTRACTION
            # --------------------------------

            logger.info("Starting OCR/text extraction file_name=%s", file_name)

            resume_data = extract_text_from_pdf(file_path)

            # --------------------------------
            # EXTRACTION FAILED
            # --------------------------------

            if "text" not in resume_data:

                logger.error("OCR/text extraction failed file_name=%s", file_name)

                return None

            logger.info(
                "Completed OCR/text extraction file_name=%s text_length=%s",
                file_name,
                len(resume_data.get("text", "")),
            )

            # --------------------------------
            # ADD METADATA
            # --------------------------------

            resume_data["category"] = category

            # --------------------------------
            # EMBEDDING
            # --------------------------------

            logger.info("Starting embedding generation file_name=%s", file_name)

            embedding = self.embedding_engine.generate_embedding(resume_data["text"])

            logger.info(
                "Completed embedding generation file_name=%s dimensions=%s",
                file_name,
                len(embedding),
            )

            # --------------------------------
            # ADD EMBEDDING
            # --------------------------------

            resume_data["embedding"] = embedding

            # --------------------------------
            # STRUCTURED PROFILE
            # --------------------------------

            logger.info("Starting structured resume parsing file_name=%s", file_name)

            profile = self.parser.build_candidate_profile(resume_data)

            if metadata_overrides:

                candidate_name = str(
                    metadata_overrides.get("candidate_name", "") or ""
                ).strip()

                email = str(metadata_overrides.get("email", "") or "").strip()

                override_category = str(
                    metadata_overrides.get("category", "") or ""
                ).strip()

                if candidate_name:

                    profile["candidate_name"] = candidate_name

                if email:

                    profile["email"] = email

                if override_category:

                    profile["category"] = override_category

            logger.info("Completed structured resume parsing file_name=%s", file_name)

            # --------------------------------
            # LLM ENRICHMENT
            # --------------------------------

            llm_data = {}

            try:

                logger.info("Starting LLM enrichment file_name=%s", file_name)

                llm_data = enrich_resume(resume_data["text"])

                logger.info(
                    "Completed LLM enrichment file_name=%s skill_count=%s",
                    file_name,
                    len(llm_data.get("technical_skills", [])),
                )

            except Exception:

                logger.exception("LLM enrichment failed file_name=%s", file_name)

            # --------------------------------
            # EXISTING SKILLS
            # --------------------------------

            existing_skills = profile.get("skills", [])

            existing_skills = [
                str(skill).strip().title() for skill in existing_skills if skill
            ]

            # --------------------------------
            # LLM SKILLS
            # --------------------------------

            llm_skills = llm_data.get("technical_skills", [])

            llm_skills = [str(skill).strip().title() for skill in llm_skills if skill]

            # --------------------------------
            # MERGE SKILLS
            # --------------------------------

            merged_skills = list(set(existing_skills + llm_skills))

            # Limit skill count
            merged_skills = merged_skills[:30]

            profile["skills"] = merged_skills

            logger.info(
                "Final merged skills file_name=%s skill_count=%s skills=%s",
                file_name,
                len(profile["skills"]),
                profile["skills"],
            )

            # --------------------------------
            # EXTRA DATABASE FIELDS
            # --------------------------------

            profile["resume_summary"] = str(llm_data.get("summary", "") or "").strip()

            profile["resume_text"] = resume_data["text"]

            profile["cleaned_text"] = resume_data["text"]

            profile["resume_file_path"] = file_path

            profile["semantic_score"] = 0.0

            profile["weighted_score"] = 0.0

            profile["recruiter_score"] = 0.0

            # --------------------------------
            # INSERT INTO DATABASE
            # --------------------------------

            logger.info("Starting DB insertion file_name=%s", file_name)

            candidate = insert_candidate(self.db, profile, embedding)

            logger.info(
                "Completed DB insertion file_name=%s candidate_id=%s",
                file_name,
                candidate.id,
            )

            logger.info(
                "Completed resume ingestion file_name=%s candidate_id=%s",
                file_name,
                candidate.id,
            )

            return candidate

        except Exception:

            logger.exception(
                "Resume ingestion failed file_name=%s file_path=%s",
                file_name,
                file_path,
            )

            self.db.rollback()

            return None
