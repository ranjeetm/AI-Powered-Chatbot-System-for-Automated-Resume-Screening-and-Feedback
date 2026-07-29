# ATS Evaluation Suite

This suite evaluates the AI-powered ATS across ranking quality, structured resume extraction, JD matching, API latency, pipeline reliability, and recruiter copilot retrieval. It uses a synthetic labeled dataset plus real database inserts, real SentenceTransformer embeddings, pgvector queries, and optional live API/LLM checks so failures point to practical product risks rather than isolated unit behavior.

## Prerequisites

Set the database URL before running DB-backed tests:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
export LOCAL_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
```

Optional variables:

```bash
export OPENROUTER_API_KEY=your_openrouter_key
export ATS_TEST_BASE_URL=http://127.0.0.1:8000
export ATS_TEST_USERNAME=ats.eval@example.com
export ATS_TEST_PASSWORD='EvalPassword123!'
```

Install evaluation dependencies:

```bash
pip install pytest pytest-asyncio httpx scikit-learn scipy numpy sentence-transformers
```

## How To Run

From the repository root:

```bash
cd backend
python -m pytest evaluation/ -v
```

Skip slow embedding, LLM, and integration checks:

```bash
python -m pytest evaluation/ -v -m "not slow"
```

Run one module:

```bash
python -m pytest evaluation/test_ranking.py -v
```

Run the standalone report generator:

```bash
python evaluation/run_eval.py
```

## Interpreting Results

Ranking tests report NDCG@10, precision@5, MRR, score spread, and an ablation check. Required thresholds are NDCG@10 >= 0.60, precision@5 >= 0.40, MRR >= 0.50, score standard deviation >= 10, max score >= 60, and min score <= 50.

Extraction tests report skill macro-F1, experience-years MAE, exact name/email accuracy, degree macro-F1, and field completeness. Required thresholds are skill F1 >= 0.65, MAE <= 2 years, name accuracy >= 80%, email accuracy >= 90%, degree F1 >= 0.60, and completeness >= 0.75.

JD matching tests verify results exist, score components are present, final scores stay in [0, 1], matched/missing skills are coherent, and JD embeddings are 384-dimensional.

API latency tests are skipped if `ATS_TEST_BASE_URL` is unreachable. Thresholds are login p95 < 1000 ms, rank-candidates p95 < 5000 ms, and jobs p95 < 500 ms.

Pipeline reliability checks embedding coverage, profile completeness, duplicate pairs, and persisted score ranges. Duplicate detection is warning-only.

Copilot tests are skipped unless `OPENROUTER_API_KEY` is set. They verify candidate retrieval, context precision, and skill/experience filters.

## Extending The Dataset

To add a new ranking case, edit `evaluation/fixtures/eval_dataset.json` and append an object to `ranking_cases` with a unique `id`, an 80-word realistic `job_description`, five labeled synthetic candidates, and at least one `copilot_queries` entry. Use relevance `3` for the ideal candidate, `2` for good partial fits, `1` for weak adjacent fits, and `0` for non-relevant candidates.
