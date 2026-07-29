"""JD matching integration evaluation.

Validates the job-description ingestion and matching path. Acceptance
thresholds: each seeded JD must return at least one match, all final scores
must be in [0, 1], score components must be present, skill explanations must
be coherent, and generated JD embeddings must be 384-dimensional.
"""

from __future__ import annotations

import pytest

from backend.db.models import CandidateProfile, JobDescription, MatchResult
from backend.repositories.jd_matching_repository import JDMatchingRepository
from backend.services.jd_matching.jd_ingestion_service import JDIngestionService
from backend.services.jd_matching.matching_service import JDMatchingService


@pytest.mark.slow
class TestJDMatching:
    async def _create_jds_and_matches(self, db_session, seed_candidates):
        repository = JDMatchingRepository()
        ingestion_service_jd = JDIngestionService(repository=repository)
        matching_service = JDMatchingService(repository=repository)
        created_jd_ids = []
        created_match_ids = []
        payloads = []

        try:
            for case in seed_candidates["ranking_cases"]:
                jd = await ingestion_service_jd.create_jd(
                    db_session,
                    title=f"Test JD {case['id']}",
                    description=case["job_description"],
                    created_by=None,
                )
                created_jd_ids.append(jd.id)
                _, matches, _ = await matching_service.match_candidates(
                    db_session,
                    job_description_id=jd.id,
                    top_k=5,
                    generate_ai_feedback=False,
                    notify_recruiter=False,
                    recruiter_email=None,
                )
                created_match_ids.extend(match.match_result_id for match in matches)
                payloads.append((jd, matches))
            return payloads, created_jd_ids, created_match_ids
        except Exception:
            self._cleanup(db_session, created_match_ids, created_jd_ids)
            raise

    def _cleanup(self, db_session, match_ids, jd_ids):
        if match_ids:
            (
                db_session.query(MatchResult)
                .filter(MatchResult.id.in_(match_ids))
                .delete(synchronize_session=False)
            )
        if jd_ids:
            (
                db_session.query(JobDescription)
                .filter(JobDescription.id.in_(jd_ids))
                .delete(synchronize_session=False)
            )
        db_session.commit()

    @pytest.mark.asyncio
    async def test_match_returns_results(self, db_session, seed_candidates):
        payloads, jd_ids, match_ids = await self._create_jds_and_matches(
            db_session,
            seed_candidates,
        )
        try:
            for jd, matches in payloads:
                print(f"jd_id={jd.id} returned_matches={len(matches)}")
                assert len(matches) >= 1
                for match in matches:
                    print(
                        f"candidate_id={match.candidate_id} "
                        f"final_score={match.final_score:.4f}"
                    )
                    assert 0.0 <= match.final_score <= 1.0
        finally:
            self._cleanup(db_session, match_ids, jd_ids)

    @pytest.mark.asyncio
    async def test_score_components_present(self, db_session, seed_candidates):
        payloads, jd_ids, match_ids = await self._create_jds_and_matches(
            db_session,
            seed_candidates,
        )
        try:
            for jd, matches in payloads:
                for match in matches:
                    print(
                        f"jd_id={jd.id} candidate_id={match.candidate_id} "
                        f"semantic={match.semantic_score} skill={match.skill_score} "
                        f"experience={match.experience_score} final={match.final_score}"
                    )
                    assert match.semantic_score is not None
                    assert match.skill_score is not None
                    assert match.experience_score is not None
                    assert match.final_score is not None
        finally:
            self._cleanup(db_session, match_ids, jd_ids)

    @pytest.mark.asyncio
    async def test_matched_missing_skills_coherence(self, db_session, seed_candidates):
        payloads, jd_ids, match_ids = await self._create_jds_and_matches(
            db_session,
            seed_candidates,
        )
        try:
            for _, matches in payloads:
                for match in matches:
                    matched = match.matched_skills or []
                    missing = match.missing_skills or []
                    assert isinstance(matched, list)
                    assert isinstance(missing, list)
                    overlap = {
                        str(skill).strip().lower()
                        for skill in matched
                    } & {
                        str(skill).strip().lower()
                        for skill in missing
                    }
                    print(
                        f"candidate_id={match.candidate_id} "
                        f"matched={matched} missing={missing} overlap={overlap}"
                    )
                    assert not overlap

                    candidate = (
                        db_session.query(CandidateProfile)
                        .filter(CandidateProfile.id == match.candidate_id)
                        .first()
                    )
                    candidate_skills = {
                        str(skill).strip().lower()
                        for skill in (candidate.skills or [])
                    }
                    for skill in matched:
                        assert str(skill).strip().lower() in candidate_skills
        finally:
            self._cleanup(db_session, match_ids, jd_ids)

    @pytest.mark.asyncio
    async def test_jd_embedding_generated(self, db_session):
        repository = JDMatchingRepository()
        ingestion_service_jd = JDIngestionService(repository=repository)
        jd = await ingestion_service_jd.create_jd(
            db_session,
            title="Test JD Embedding",
            description=(
                "Python backend engineer role requiring FastAPI, PostgreSQL, "
                "Docker, Redis, and production API experience."
            ),
            created_by=None,
        )
        try:
            fetched = repository.get_job_description(db_session, jd.id)
            embedding = list(fetched.embedding) if fetched.embedding is not None else []
            print(f"jd_id={jd.id} embedding_dimensions={len(embedding)}")
            assert fetched.embedding is not None
            assert len(embedding) == 384
        finally:
            (
                db_session.query(JobDescription)
                .filter(JobDescription.id == jd.id)
                .delete(synchronize_session=False)
            )
            db_session.commit()
