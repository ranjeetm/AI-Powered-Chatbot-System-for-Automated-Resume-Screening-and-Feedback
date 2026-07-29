# ATS Evaluation Suite Report

## What Was Built

Created a complete evaluation suite under `backend/evaluation/` for the AI-powered ATS. The suite covers:

- Candidate ranking quality
- Structured resume extraction accuracy
- JD ingestion and matching correctness
- API latency smoke checks
- Pipeline reliability and production-data sanity
- Recruiter copilot retrieval quality
- Programmatic evaluation reporting

## Files Added

- `backend/evaluation/__init__.py`
- `backend/evaluation/fixtures/eval_dataset.json`
- `backend/evaluation/conftest.py`
- `backend/evaluation/test_ranking.py`
- `backend/evaluation/test_extraction.py`
- `backend/evaluation/test_jd_matching.py`
- `backend/evaluation/test_api_latency.py`
- `backend/evaluation/test_pipeline_reliability.py`
- `backend/evaluation/test_copilot.py`
- `backend/evaluation/run_eval.py`
- `backend/evaluation/README.md`

## How To Run

```bash
cd backend
python -m pytest evaluation/ -v
```

To skip slow embedding/API/LLM tests:

```bash
python -m pytest evaluation/ -v -m "not slow"
```

To generate a JSON report:

```bash
python evaluation/run_eval.py
```

## Key Thresholds

- Ranking: `NDCG@10 >= 0.60`, `Precision@5 >= 0.40`, `MRR >= 0.50`
- Extraction: `Skill F1 >= 0.65`, `Experience MAE <= 2.0`, `Completeness >= 0.75`
- JD matching: final scores must be in `[0.0, 1.0]`
- API latency: login p95 `< 1000ms`, ranking p95 `< 5000ms`, jobs p95 `< 500ms`
- Pipeline reliability: embedding null rate `<= 10%`, completeness `>= 70%`

## Notes

The suite uses real embeddings and real DB inserts, so `DATABASE_URL` must point to a PostgreSQL database with pgvector enabled. Copilot tests are skipped unless `OPENROUTER_API_KEY` is set. API latency tests are skipped unless the backend server is reachable at `ATS_TEST_BASE_URL`.

## Validation Run

Executed from `backend/`:

```bash
python -m pytest evaluation/ -v
```

Result:

```text
25 passed, 391 warnings in 335.69s
```

Also executed:

```bash
python evaluation/run_eval.py
```

Result:

```text
25 passed, 0 failed, 0 skipped
Pass rate: 100.0%
```

JSON report:

```text
backend/evaluation/results/eval_report_2026-05-17T08-57-07Z00-00.json
```

One setup cleanup was performed before the final run: legacy sample rows inserted earlier by `test_db_insert.py` with `email='ranjeet@test.com'` and `file_name='resume.pdf'` were removed so the score-range reliability check reflected the actual ATS data rather than old script artifacts.
