from backend.embeddings.embedding_engine import EmbeddingEngine

from backend.db.database import SessionLocal

from backend.repositories.candidate_repository import (
    semantic_search,
    get_candidate_by_id,
)

from backend.scoring.profile_scorer import ProfileScorer


class CandidateRankingService:

    def __init__(self):

        self.embedding_engine = EmbeddingEngine()

        self.db = SessionLocal()

        self.profile_scorer = ProfileScorer()

    # --------------------------------
    # RANK CANDIDATES
    # --------------------------------

    def rank_candidates(self, job_description, top_k=10):

        # --------------------------------
        # EMBEDDING
        # --------------------------------

        query_embedding = self.embedding_engine.generate_embedding(job_description).tolist()

        # --------------------------------
        # VECTOR SEARCH
        # --------------------------------

        semantic_results = semantic_search(
            db=self.db, query_embedding=query_embedding, limit=top_k
        )

        ranked_candidates = []
        required_experience = self.profile_scorer.extract_required_experience(
            job_description
        )

        # --------------------------------
        # PROCESS CANDIDATES
        # --------------------------------

        for result in semantic_results:

            candidate_id = result[0]

            semantic_distance = result[5]

            semantic_similarity = 1 - semantic_distance

            # --------------------------------
            # FETCH CANDIDATE
            # --------------------------------

            candidate = get_candidate_by_id(self.db, candidate_id)

            if not candidate:
                continue

            # --------------------------------
            # STRUCTURED SCORING
            # --------------------------------

            skill_match = self.profile_scorer.calculate_skill_match(
                candidate.skills or [],
                job_description,
                candidate_text=(
                    candidate.cleaned_text
                    or candidate.resume_text
                    or candidate.resume_summary
                ),
            )

            title_match = self.profile_scorer.calculate_title_match(
                candidate.job_titles or [],
                job_description.lower(),
                candidate_category=candidate.category,
                candidate_skills=candidate.skills or [],
            )

            experience_match = self.profile_scorer.calculate_experience_match(
                candidate.experience_years or 0,
                required_experience=required_experience
            )

            # --------------------------------
            # FINAL SCORE
            # --------------------------------

            final_score = self.profile_scorer.calculate_final_score(
                semantic_similarity, skill_match, title_match, experience_match
            )

            ranked_candidates.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.candidate_name,
                    "category": candidate.category,
                    "skills": candidate.skills,
                    "experience_years": candidate.experience_years,
                    "semantic_similarity": round(semantic_similarity, 4),
                    "skill_match": round(skill_match, 4),
                    "title_match": round(title_match, 4),
                    "experience_match": round(experience_match, 4),
                    "required_experience_years": required_experience,
                    "final_score": round(final_score, 4),
                }
            )

        # --------------------------------
        # SORT BY FINAL SCORE
        # --------------------------------

        ranked_candidates = sorted(
            ranked_candidates, key=lambda x: x["final_score"], reverse=True
        )

        return ranked_candidates
