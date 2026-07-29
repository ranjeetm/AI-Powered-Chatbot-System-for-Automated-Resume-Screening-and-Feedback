"""Ranking quality evaluation.

Measures NDCG@10, precision@5, MRR, score distribution, and a scoring ablation.
Acceptance thresholds: NDCG@10 >= 0.60 per case, precision@5 >= 0.40 per
case, MRR >= 0.50, score std-dev >= 10, max score >= 60, min score <= 50, and
full scoring should be at least as good as the semantic-only ablation.
"""

from __future__ import annotations

import statistics

import pytest
from sklearn.metrics import ndcg_score

from backend.scoring.profile_scorer import ProfileScorer


def _score_to_100(score):
    value = float(score or 0)
    return value * 100.0 if value <= 1.0 else value


def _case_relevance(case):
    return {
        candidate["candidate_id"]: candidate["relevance"]
        for candidate in case["candidates"]
    }


def _aligned_scores(case, results):
    relevance_by_id = _case_relevance(case)
    score_by_id = {
        result["candidate_id"]: _score_to_100(result.get("final_score", 0))
        for result in results
    }
    candidate_ids = list(relevance_by_id.keys())
    true_relevance = [relevance_by_id[candidate_id] for candidate_id in candidate_ids]
    predicted_scores = [score_by_id.get(candidate_id, 0.0) for candidate_id in candidate_ids]
    return true_relevance, predicted_scores


def _mean_ndcg(dataset, ranking_service):
    scores = []
    for case in dataset["ranking_cases"]:
        results = ranking_service.rank_candidates(
            job_description=case["job_description"],
            top_k=10,
        )
        true_relevance, predicted_scores = _aligned_scores(case, results)
        scores.append(float(ndcg_score([true_relevance], [predicted_scores], k=10)))
    return statistics.mean(scores)


@pytest.mark.slow
class TestRankingQuality:
    def test_ndcg_at_10(self, seed_candidates, ranking_service):
        print("case_id | ndcg | pass/fail")
        for case in seed_candidates["ranking_cases"]:
            results = ranking_service.rank_candidates(
                job_description=case["job_description"],
                top_k=10,
            )
            true_relevance, predicted_scores = _aligned_scores(case, results)
            ndcg = float(ndcg_score([true_relevance], [predicted_scores], k=10))
            status = "pass" if ndcg >= 0.60 else "fail"
            print(f"{case['id']} | {ndcg:.3f} | {status}")
            assert ndcg >= 0.60

    def test_precision_at_5(self, seed_candidates, ranking_service):
        for case in seed_candidates["ranking_cases"]:
            results = ranking_service.rank_candidates(
                job_description=case["job_description"],
                top_k=10,
            )
            relevance_by_id = _case_relevance(case)
            relevant_count = sum(
                1
                for result in results[:5]
                if relevance_by_id.get(result["candidate_id"], 0) >= 2
            )
            precision = relevant_count / 5
            print(f"{case['id']} precision@5={precision:.2f} relevant_top5={relevant_count}")
            assert precision >= 0.40

    def test_mrr(self, seed_candidates, ranking_service):
        reciprocal_ranks = []
        for case in seed_candidates["ranking_cases"]:
            results = ranking_service.rank_candidates(
                job_description=case["job_description"],
                top_k=10,
            )
            relevance_by_id = _case_relevance(case)
            rank = None
            for index, result in enumerate(results, start=1):
                if relevance_by_id.get(result["candidate_id"]) == 3:
                    rank = index
                    break
            reciprocal = 0.0 if rank is None else 1.0 / rank
            reciprocal_ranks.append(reciprocal)
            print(f"{case['id']} best_relevant_rank={rank} reciprocal_rank={reciprocal:.3f}")

        mrr = statistics.mean(reciprocal_ranks)
        print(f"MRR={mrr:.3f}")
        assert mrr >= 0.50

    def test_score_distribution(self, seed_candidates, ranking_service):
        scores = []
        for case in seed_candidates["ranking_cases"]:
            results = ranking_service.rank_candidates(
                job_description=case["job_description"],
                top_k=10,
            )
            scores.extend(_score_to_100(result["final_score"]) for result in results)

        std_dev = statistics.pstdev(scores)
        max_score = max(scores)
        min_score = min(scores)
        print(
            f"score_distribution std_dev={std_dev:.2f} "
            f"max={max_score:.2f} min={min_score:.2f}"
        )
        assert std_dev >= 10.0
        assert max_score >= 60.0
        assert min_score <= 50.0

    def test_ablation_semantic_only(self, seed_candidates, ranking_service, monkeypatch):
        monkeypatch.setattr(
            ProfileScorer,
            "calculate_skill_match",
            lambda self, candidate_skills, jd_text: 0.5,
        )
        monkeypatch.setattr(
            ProfileScorer,
            "calculate_title_match",
            lambda self, candidate_titles, jd_text: 0.5,
        )
        semantic_only_ndcg = _mean_ndcg(seed_candidates, ranking_service)
        monkeypatch.undo()
        full_ndcg = _mean_ndcg(seed_candidates, ranking_service)
        print(
            f"semantic_only_ndcg={semantic_only_ndcg:.3f} "
            f"full_ndcg={full_ndcg:.3f}"
        )
        assert full_ndcg >= semantic_only_ndcg
