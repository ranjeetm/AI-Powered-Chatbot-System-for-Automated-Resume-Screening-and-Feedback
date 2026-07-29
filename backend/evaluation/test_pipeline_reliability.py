"""Pipeline reliability and production-data sanity evaluation.

Checks embedding coverage, structured profile completeness, near-duplicate
embedding pairs, and score ranges in candidate_profiles. Acceptance thresholds:
embedding null rate <= 10%, mean profile completeness >= 70%, duplicate
detection is warning-only, and persisted score fields must stay in [0, 1].
"""

from __future__ import annotations

import statistics

import pytest
from sqlalchemy import text

from backend.db.models import CandidateProfile


def _is_filled(value):
    if value is None:
        return False
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return bool(str(value).strip())


class TestPipelineReliability:
    def test_embedding_coverage(self, db_session):
        null_count = db_session.execute(
            text("SELECT COUNT(*) FROM candidate_profiles WHERE embedding IS NULL")
        ).scalar()
        total = db_session.execute(
            text("SELECT COUNT(*) FROM candidate_profiles")
        ).scalar()
        if total == 0:
            pytest.skip("No candidates in database - seed data first")

        null_rate = null_count / total
        print(f"Embedding coverage: {(1 - null_rate) * 100:.1f}%")
        assert null_rate <= 0.10

    def test_profile_completeness(self, db_session):
        rows = db_session.query(CandidateProfile).all()
        if not rows:
            pytest.skip("No candidates in database - seed data first")

        fields = [
            "candidate_name",
            "skills",
            "experience_years",
            "embedding",
            "resume_text",
            "job_titles",
        ]
        field_fills = {field: 0 for field in fields}
        row_scores = []

        for row in rows:
            filled = 0
            for field in fields:
                value = getattr(row, field)
                ok = _is_filled(value)
                filled += int(ok)
                field_fills[field] += int(ok)
            row_scores.append(filled / len(fields))

        for field in fields:
            fill_rate = field_fills[field] / len(rows)
            print(f"{field}_fill_rate={fill_rate:.2f}")

        mean_completeness = statistics.mean(row_scores)
        print(f"mean_profile_completeness={mean_completeness:.2f}")
        assert mean_completeness >= 0.70

    def test_duplicate_detection(self, db_session):
        rows = db_session.execute(
            text(
                """
                SELECT a.id, b.id, (a.embedding <-> b.embedding) AS dist
                FROM candidate_profiles a, candidate_profiles b
                WHERE
                    a.id < b.id
                    AND a.embedding IS NOT NULL
                    AND b.embedding IS NOT NULL
                    AND (a.embedding <-> b.embedding) < 0.02
                """
            )
        ).fetchall()
        print(f"Near-duplicate pairs found: {len(rows)}")

    def test_score_range_sanity(self, db_session):
        rows = db_session.query(CandidateProfile).all()
        if not rows:
            pytest.skip("No candidates in database - seed data first")

        for field in ["semantic_score", "weighted_score", "recruiter_score"]:
            values = [
                float(getattr(row, field))
                for row in rows
                if getattr(row, field) is not None
            ]
            if not values:
                print(f"{field}: no values set")
                continue
            print(
                f"{field}: count={len(values)} min={min(values):.4f} "
                f"max={max(values):.4f}"
            )
            assert all(0.0 <= value <= 1.0 for value in values)
