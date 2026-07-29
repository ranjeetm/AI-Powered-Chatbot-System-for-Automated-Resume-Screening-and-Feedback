"""Shared fixtures for the ATS evaluation suite.

Evaluation requirements: pytest, pytest-asyncio, httpx, scikit-learn, scipy,
numpy, sentence-transformers.
"""

from __future__ import annotations

import asyncio
import copy
import inspect
import json
import sys
from pathlib import Path

import pytest
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db.crud import insert_candidate
from backend.db.database import SessionLocal
from backend.db.models import CandidateProfile
from backend.services.candidate_ranking_service import CandidateRankingService
from backend.services.resume_ingestion_service import ResumeIngestionService

try:
    import pytest_asyncio  # noqa: F401

    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: tests that load embeddings, query an LLM, or run integration flows",
    )
    config.addinivalue_line(
        "markers",
        "asyncio: async tests; pytest-asyncio is recommended",
    )


def pytest_pyfunc_call(pyfuncitem):
    if HAS_PYTEST_ASYNCIO:
        return None

    if "asyncio" not in pyfuncitem.keywords:
        return None

    test_func = pyfuncitem.obj
    if not inspect.iscoroutinefunction(test_func):
        return None

    kwargs = {
        arg: pyfuncitem.funcargs[arg]
        for arg in pyfuncitem._fixtureinfo.argnames
    }
    asyncio.run(test_func(**kwargs))
    return True


@pytest.fixture(scope="module")
def eval_dataset():
    dataset_path = Path(__file__).resolve().parent / "fixtures" / "eval_dataset.json"
    with dataset_path.open("r", encoding="utf-8") as handle:
        return copy.deepcopy(json.load(handle))


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def ranking_service():
    service = CandidateRankingService()
    try:
        yield service
    finally:
        if getattr(service, "db", None) is not None:
            service.db.close()


@pytest.fixture
def ingestion_service():
    service = ResumeIngestionService()
    try:
        yield service
    finally:
        service.close()


@pytest.fixture
def seed_candidates(db_session, eval_dataset):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    seeded_ids: list[int] = []

    try:
        for case in eval_dataset["ranking_cases"]:
            for index, candidate in enumerate(case["candidates"], start=1):
                profile = candidate["synthetic_profile"]
                resume_text = profile["resume_text"]
                embedding = model.encode(resume_text)
                row = insert_candidate(
                    db_session,
                    {
                        "file_name": f"{case['id']}_{index}.txt",
                        "candidate_name": profile["candidate_name"],
                        "email": (
                            profile["candidate_name"]
                            .lower()
                            .replace(" ", ".")
                            + "@eval.local"
                        ),
                        "category": f"evaluation_{case['id']}",
                        "skills": profile["skills"],
                        "experience_years": profile["experience_years"],
                        "job_titles": profile["job_titles"],
                        "degrees": profile["degrees"],
                        "resume_summary": resume_text[:450],
                        "resume_text": resume_text,
                        "cleaned_text": resume_text,
                        "resume_file_path": f"synthetic://{case['id']}/{index}",
                        "semantic_score": 0.0,
                        "weighted_score": 0.0,
                        "recruiter_score": 0.0,
                    },
                    embedding,
                )
                candidate["candidate_id"] = row.id
                seeded_ids.append(row.id)

        yield eval_dataset
    finally:
        for candidate_id in seeded_ids:
            row = (
                db_session.query(CandidateProfile)
                .filter(CandidateProfile.id == candidate_id)
                .first()
            )
            if row:
                db_session.delete(row)
        db_session.commit()
