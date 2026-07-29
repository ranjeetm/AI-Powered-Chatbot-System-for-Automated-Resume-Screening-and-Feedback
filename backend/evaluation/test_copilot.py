"""Recruiter copilot retrieval quality evaluation.

Evaluates RAG retrieval candidates and metadata filters. Acceptance thresholds:
every labeled query retrieves at least one candidate, context_precision@6 >=
0.50, skill filters return Python-bearing profiles, and experience filters only
return candidates with at least the requested experience unless the value is
unknown.
"""

from __future__ import annotations

import os

import pytest
from sentence_transformers import SentenceTransformer

from backend.repositories.chatbot_repository import ChatbotRepository


pytestmark = [
    pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY is not set",
    ),
    pytest.mark.slow,
]


class TestCopilotQuality:
    def _search(self, db_session, query, filters=None, top_n=6):
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(query)
        chatbot_repo = ChatbotRepository()
        return chatbot_repo.hybrid_candidate_search(
            db=db_session,
            query=query,
            query_embedding=embedding.tolist(),
            top_n=top_n,
            filters=filters or {},
        )

    def _queries(self, seed_candidates):
        for case in seed_candidates["ranking_cases"]:
            for query in case["copilot_queries"]:
                yield case, query

    def test_retrieval_returns_candidates(self, db_session, seed_candidates):
        for _, query in self._queries(seed_candidates):
            results = self._search(db_session, query["query"])
            print(f"query={query['query']!r} result_count={len(results)}")
            assert len(results) >= 1

    def test_context_precision(self, db_session, seed_candidates):
        total_queries = 0
        matched_queries = 0
        for _, query in self._queries(seed_candidates):
            total_queries += 1
            results = self._search(db_session, query["query"])
            expected = {
                name.strip().lower()
                for name in query["expected_candidate_names"]
            }
            returned = {
                str(result.get("candidate_name") or "").strip().lower()
                for result in results
            }
            matched = bool(expected & returned)
            matched_queries += int(matched)
            print(
                f"query={query['query']!r} matched={matched} "
                f"expected={sorted(expected)} returned={sorted(returned)}"
            )

        context_precision = matched_queries / total_queries
        print(f"context_precision@6={context_precision:.2f}")
        assert context_precision >= 0.50

    def test_filter_by_skills(self, db_session, seed_candidates):
        results = self._search(
            db_session,
            "Python candidate",
            filters={"skills": ["Python"]},
            top_n=10,
        )
        print(f"python_filter_result_count={len(results)}")
        assert len(results) >= 1
        for result in results:
            skills = {
                str(skill).strip().lower()
                for skill in (result.get("skills") or [])
            }
            resume_text = str(result.get("resume_text") or "").lower()
            assert "python" in skills or "python" in resume_text

    def test_filter_by_experience(self, db_session, seed_candidates):
        results = self._search(
            db_session,
            "senior experienced candidate",
            filters={"min_experience_years": 5},
            top_n=10,
        )
        print(f"experience_filter_result_count={len(results)}")
        assert len(results) >= 1
        for result in results:
            years = result.get("experience_years")
            assert years is None or years >= 5
