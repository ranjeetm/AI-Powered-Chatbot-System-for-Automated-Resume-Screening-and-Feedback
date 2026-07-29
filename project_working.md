# Project Working: AI Resume Screening ATS

## 1. Project Summary

This project is an AI-powered Applicant Tracking System (ATS). It helps recruiters upload resumes, parse candidate information, rank candidates against job descriptions, shortlist or reject candidates, and use an AI recruiter copilot to ask questions about the candidate database.

It also supports candidates by showing public jobs and allowing them to apply with a PDF resume.

The project has three main parts:

- Frontend: Next.js recruiter/candidate portal.
- Backend: FastAPI API server with resume parsing, ranking, auth, JD matching, and chatbot services.
- Data layer: PostgreSQL with pgvector for normal relational data plus semantic vector search.

## 2. Technology Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- Next.js App Router
- Local API proxy at `/api/backend/*`

Important frontend files:

- `frontend/app/page.tsx`: loads the ATS portal.
- `frontend/components/ats/AtsPortal.tsx`: main UI for candidate and recruiter workflows.
- `frontend/lib/api.ts`: typed API client used by the UI.
- `frontend/app/api/backend/[...path]/route.ts`: forwards frontend API calls to FastAPI.

### Backend

- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Alembic
- Celery
- Redis
- JWT authentication with `python-jose`
- Password hashing with Passlib and bcrypt

Important backend files:

- `backend/api/main.py`: FastAPI app entry point.
- `backend/api/auth.py`: recruiter register and login routes.
- `backend/api/routes/upload.py`: resume upload and candidate application routes.
- `backend/api/routes/ranking.py`: quick candidate ranking route.
- `backend/api/routes/jobs.py`: job posting routes.
- `backend/api/routes/candidates.py`: candidate details and resume download routes.
- `backend/api/routes/jd_matching.py`: job description ingestion and matching routes.
- `backend/api/routes/chatbot.py`: recruiter copilot chat routes.
- `backend/api/routes/shortlist.py`: shortlist, unshortlist, and feedback routes.

### AI, NLP, and Parsing

- SentenceTransformers: `all-MiniLM-L6-v2` embeddings.
- pgvector: vector similarity search inside PostgreSQL.
- spaCy: NLP support.
- PyMuPDF, pdfplumber, pdf2image, pytesseract: PDF text/OCR extraction.
- OpenRouter API: LLM enrichment, recruiter copilot answers, and AI feedback.
- scikit-learn, numpy, pandas, scipy: scoring and evaluation support.

Important AI/parsing files:

- `backend/parser/parser.py`: extracts text from PDF resumes and JD PDFs.
- `backend/extraction/structured_parser.py`: builds structured candidate profiles.
- `backend/extraction/skill_extractor.py`: extracts skills.
- `backend/services/resume_ingestion_service.py`: full resume ingestion pipeline.
- `backend/services/llm_enrichment.py`: optional LLM enrichment.
- `backend/embeddings/embedding_engine.py`: embedding helper.
- `backend/scoring/profile_scorer.py`: quick ranking score logic.
- `backend/services/chatbot/*`: recruiter copilot retrieval, reranking, context, and LLM response logic.

### Database and Infrastructure

- PostgreSQL 16 with pgvector.
- Redis for Celery broker and result backend.
- Docker Compose for Postgres, backend, and frontend.
- Local filesystem storage for uploaded PDF resumes.

Important database files:

- `backend/db/database.py`: database URL resolution and SQLAlchemy engine.
- `backend/db/models.py`: candidate, job, JD, and match result tables.
- `backend/db/auth_models.py`: recruiter user table.
- `backend/db/initializer.py`: creates pgvector extension and database tables.
- `backend/db/session.py`: request-scoped database sessions.
- `backend/repositories/*`: database query layer.

## 3. Main Database Tables

### `users`

Stores recruiter login accounts.

Main fields:

- `id`
- `email`
- `full_name`
- `hashed_password`
- `created_at`

### `candidate_profiles`

Stores parsed resume data and candidate embeddings.

Main fields:

- Basic details: `candidate_name`, `email`, `phone`, `location`
- Links: `linkedin_url`, `github_url`
- Resume structure: `skills`, `job_titles`, `education`, `projects`, `experience`, `sections`
- Resume text: `resume_text`, `cleaned_text`, `resume_summary`, `resume_file_path`
- Scores: `semantic_score`, `weighted_score`, `recruiter_score`
- Shortlist fields: `is_shortlisted`, `shortlist_updated_at`, `rejection_feedback`
- Vector field: `embedding Vector(384)`

### `job_postings`

Stores jobs shown in the candidate portal.

Main fields:

- `title`
- `department`
- `location`
- `type`
- `description`
- `skills`
- `created_at`

### `job_descriptions`

Stores recruiter-created or uploaded JDs for AI matching.

Main fields:

- `title`
- `description`
- `extracted_skills`
- `inferred_category`
- `inferred_seniority`
- `embedding Vector(384)`
- `created_by`
- `created_at`

### `match_results`

Stores candidate match results generated for a JD.

Main fields:

- `candidate_id`
- `job_description_id`
- `semantic_score`
- `skill_score`
- `experience_score`
- `final_score`
- `matched_skills`
- `missing_skills`
- `strengths`
- `ai_feedback`
- `created_at`

## 4. How The Project Works End To End

### Step 1: App Starts

Backend startup begins in `backend/api/main.py`.

When FastAPI starts:

1. `initialize_database()` runs.
2. The pgvector extension is created if missing.
3. SQLAlchemy creates known tables if missing.
4. Compatibility columns are added for older local databases.
5. API routers are registered.
6. CORS is enabled for local frontend ports.

Frontend startup begins in `frontend/app/page.tsx`, which renders `AtsPortal`.

The frontend does not call FastAPI directly. It calls:

```text
/api/backend/*
```

That request is handled by:

```text
frontend/app/api/backend/[...path]/route.ts
```

The proxy forwards the request to one of these backend URLs:

```text
http://127.0.0.1:8000
http://localhost:8000
http://127.0.0.1:8001
http://localhost:8001
```

### Step 2: Recruiter Registers And Logs In

Routes:

- `POST /register`
- `POST /login`

Flow:

1. Recruiter creates an account.
2. Password is hashed and stored in `users`.
3. Recruiter logs in with email and password.
4. Backend returns a JWT access token.
5. Frontend stores the token in `localStorage`.
6. Protected API calls send `Authorization: Bearer <token>`.

Protected recruiter features include resume upload, ranking, candidate details, jobs creation, JD matching, shortlist actions, and recruiter copilot chat.

### Step 3: Candidate Views Jobs And Applies

Routes:

- `GET /jobs`
- `POST /candidate-apply`

Flow:

1. Candidate opens the candidate portal.
2. Frontend loads public jobs from `GET /jobs`.
3. Candidate selects a job and uploads a PDF resume.
4. Backend validates that the uploaded file is a PDF.
5. Resume is saved to `RESUME_UPLOAD_DIR`.
6. Backend queues `process_resume_task` with metadata overrides:
   - candidate name
   - candidate email
   - selected job title as category
7. Celery worker processes the resume asynchronously.
8. Parsed candidate profile is inserted into `candidate_profiles`.

### Step 4: Recruiter Uploads Resumes

Route:

- `POST /upload-resume`

Flow:

1. Recruiter uploads a PDF.
2. Backend validates the file extension.
3. File is saved locally.
4. Backend queues `backend.tasks.resume_tasks.process_resume_task`.
5. Celery worker picks up the job.
6. `ResumeIngestionService.process_resume()` performs the complete ingestion pipeline.

The upload API only queues processing. For end-to-end processing, Redis and a Celery worker must be running.

### Step 5: Resume Ingestion Pipeline

Main file:

- `backend/services/resume_ingestion_service.py`

Pipeline:

1. Read PDF path and file name.
2. Extract resume text using `extract_text_from_pdf()`.
3. Generate a 384-dimensional embedding using `all-MiniLM-L6-v2`.
4. Build a structured candidate profile:
   - name
   - email
   - phone
   - location
   - skills
   - titles
   - degrees
   - education
   - projects
   - experience
   - sections
5. Apply metadata overrides if the resume came from candidate application.
6. Try optional OpenRouter LLM enrichment.
7. Merge parser skills with LLM skills.
8. Store resume summary, full text, file path, default scores, and embedding.
9. Insert final candidate into PostgreSQL.

### Step 6: Recruiter Creates Jobs

Routes:

- `GET /jobs`
- `POST /jobs`

Flow:

1. Recruiter opens job management.
2. Recruiter creates a job with title, department, location, type, description, and skills.
3. Backend stores the job in `job_postings`.
4. Candidate portal can show the job immediately.

### Step 7: Quick Candidate Ranking

Route:

- `POST /rank-candidates`

Flow:

1. Recruiter enters or selects a job description.
2. Backend embeds the job description using SentenceTransformers.
3. PostgreSQL pgvector searches candidates by embedding distance.
4. For each candidate, backend calculates:
   - semantic similarity
   - skill match
   - title/category match
   - experience match
5. `ProfileScorer` combines those into a final score.
6. Backend returns sorted ranked candidates.
7. Frontend displays candidate score breakdowns and can open candidate details.

### Step 8: JD Matching Workflow

Routes:

- `POST /jd-matching/job-descriptions`
- `POST /jd-matching/job-descriptions/upload`
- `GET /jd-matching/job-descriptions`
- `POST /jd-matching/match`
- `POST /jd-matching/email`

Flow:

1. Recruiter creates a JD by pasting text or uploading `.txt`, `.md`, or `.pdf`.
2. Backend extracts JD text if uploaded as PDF.
3. Backend extracts skills, infers category/seniority, and creates a JD embedding.
4. JD is stored in `job_descriptions`.
5. Recruiter runs matching.
6. Backend performs hybrid candidate search:
   - pgvector semantic similarity
   - PostgreSQL keyword ranking
   - recruiter score boost
7. Backend calculates:
   - semantic score
   - skill score
   - experience score
   - recruiter score
   - final score
8. Optional AI feedback is generated.
9. Match results are stored in `match_results`.
10. Recruiter can email match summaries through EmailJS if configured.

JD matching final score currently uses this weighting:

```text
semantic_score  * 0.45
skill_score     * 0.30
experience_score * 0.15
recruiter_score * 0.10
```

### Step 9: Recruiter Opens Candidate Details

Routes:

- `GET /candidate/{candidate_id}`
- `GET /candidate-resume/{candidate_id}`

Flow:

1. Recruiter clicks a candidate.
2. Backend loads structured profile from `candidate_profiles`.
3. Frontend shows contact info, skills, experience, projects, education, summary, and shortlist state.
4. Resume download resolves the original stored PDF path and returns a PDF response.

### Step 10: Shortlist And Rejection Feedback

Routes:

- `POST /candidates/{candidate_id}/shortlist`
- `POST /candidates/{candidate_id}/unshortlist`
- `POST /candidates/{candidate_id}/feedback-suggestion`

Flow:

1. Recruiter shortlists a candidate.
2. Backend sets `is_shortlisted = true`.
3. Optional notification email is sent if EmailJS is configured.
4. Recruiter can unshortlist with feedback.
5. Backend stores rejection feedback and updates shortlist timestamp.
6. Backend can generate feedback suggestions using candidate/JD data.

### Step 11: AI Recruiter Copilot

Routes:

- `POST /recruiter-copilot/chat`
- `POST /recruiter-copilot/chat/stream`

Flow:

1. Recruiter asks a question like:
   - "Show Python candidates with 3+ years experience."
   - "Compare the top two data science candidates."
   - "Who is best for this JD?"
2. Backend detects intent.
3. Retrieval service builds a search query, optionally including job context.
4. Query is embedded.
5. Hybrid candidate search retrieves relevant candidates.
6. Reranker reorders candidates using skills, query match, semantic score, and metadata.
7. Context builder creates evidence-based prompt context.
8. OpenRouter generates the answer if configured.
9. If OpenRouter is not configured or fails, fallback formatter returns a deterministic answer.
10. Frontend shows the answer plus candidate evidence cards.

Streaming chat uses Server-Sent Events with:

- metadata event
- token events
- done event

## 5. API Endpoint Summary

### Auth

- `POST /register`: create recruiter account.
- `POST /login`: login and receive JWT token.

### Jobs

- `GET /jobs`: list public jobs.
- `POST /jobs`: create recruiter job.

### Uploads

- `POST /upload-resume`: recruiter resume upload.
- `POST /candidate-apply`: candidate application upload.

### Candidates

- `GET /candidate/{candidate_id}`: candidate profile details.
- `GET /candidate-resume/{candidate_id}`: download original resume PDF.

### Ranking

- `POST /rank-candidates`: rank candidates for a job description.

### JD Matching

- `POST /jd-matching/job-descriptions`: create pasted JD.
- `POST /jd-matching/job-descriptions/upload`: upload JD file.
- `GET /jd-matching/job-descriptions`: list saved JDs.
- `POST /jd-matching/match`: run candidate matching.
- `POST /jd-matching/email`: send match summary email.

### Shortlist

- `POST /candidates/{candidate_id}/shortlist`: shortlist candidate.
- `POST /candidates/{candidate_id}/unshortlist`: remove candidate from shortlist.
- `POST /candidates/{candidate_id}/feedback-suggestion`: generate rejection feedback suggestion.

### Recruiter Copilot

- `POST /recruiter-copilot/chat`: normal AI chat response.
- `POST /recruiter-copilot/chat/stream`: streaming AI chat response.

## 6. Environment Variables

Backend variables:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
LOCAL_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_CHAT_MODEL=openai/gpt-4o-mini
RESUME_UPLOAD_DIR=/tmp/resume_project_uploads
EMAILJS_SERVICE_ID=your_service_id
EMAILJS_TEMPLATE_ID=your_template_id
EMAILJS_PUBLIC_KEY=your_public_key
EMAILJS_PRIVATE_KEY=your_private_key_optional
```

Frontend variables:

```env
BACKEND_API_URL=http://127.0.0.1:8000
```

Notes:

- `OPENROUTER_API_KEY` is required for best LLM enrichment and copilot output.
- EmailJS variables are required only for email notifications.
- Resume upload and candidate application require Redis plus a Celery worker.
- `docker-compose.yml` expects `backend/.env` and `frontend/.env.local` when running containers.

## 7. How To Run Locally

### Option A: Local Development

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL with Docker:

```bash
docker compose up -d postgres
```

Start Redis separately if it is not already running:

```bash
redis-server
```

Start Celery worker:

```bash
celery -A backend.core.celery_app.celery_app worker --loglevel=info
```

Start FastAPI:

```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Start frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

### Option B: Docker Compose

Run:

```bash
docker compose up --build
```

Container ports:

- Frontend: `http://localhost:3001`
- Backend: `http://localhost:8001`
- Postgres: `localhost:5433`

Important: the current `docker-compose.yml` defines Postgres, backend, and frontend. It does not define Redis or a Celery worker service. Resume processing will be queued but not completed unless Redis and a Celery worker are also running.

## 8. Common User Workflows

### Candidate Workflow

```text
Candidate opens frontend
-> Views jobs from GET /jobs
-> Selects a job
-> Uploads PDF resume through POST /candidate-apply
-> Resume is queued
-> Celery parses and stores candidate profile
-> Recruiter can rank and review candidate
```

### Recruiter Resume Upload Workflow

```text
Recruiter logs in
-> Uploads PDF through POST /upload-resume
-> Backend saves file
-> Celery task starts
-> Text is extracted from PDF
-> Structured resume fields are parsed
-> Embedding is generated
-> Optional LLM enrichment runs
-> Candidate is inserted into PostgreSQL
```

### Recruiter Ranking Workflow

```text
Recruiter provides JD
-> Backend embeds JD
-> pgvector finds semantically similar resumes
-> Scoring engine checks skills, title/category, and experience
-> Backend returns sorted candidates
-> Recruiter opens profile, downloads resume, or shortlists candidate
```

### Recruiter JD Matching Workflow

```text
Recruiter saves or uploads JD
-> Backend extracts JD skills and embedding
-> Recruiter runs match
-> Backend performs hybrid vector + keyword search
-> Candidate match scores are calculated
-> Optional AI feedback is generated
-> Match results are stored
-> Recruiter can email summary
```

### Recruiter Copilot Workflow

```text
Recruiter asks question
-> Backend embeds the query
-> Hybrid retrieval finds candidates
-> Reranker builds evidence list
-> Context builder prepares prompt
-> OpenRouter generates answer
-> Frontend displays answer and evidence cards
```

## 9. Testing And Evaluation

The repo contains focused tests for parsing, extraction, ranking, embeddings, scoring, JD matching, and evaluation.

Example commands:

```bash
python -m pytest
python -m pytest test_embeddings.py
python -m pytest test_jd_matching_scoring.py
python backend/evaluation/run_eval.py
```

Evaluation-related files:

- `backend/evaluation/metrics.py`
- `backend/evaluation/benchmark_runner.py`
- `backend/evaluation/run_eval.py`
- `backend/evaluation/fixtures/eval_dataset.json`
- `run_benchmarks.py`

## 10. Current Practical Notes

- Only PDF resumes are accepted for resume upload and candidate application.
- JD upload supports `.txt`, `.md`, and `.pdf`.
- The embedding size is 384 because `all-MiniLM-L6-v2` is used.
- `initialize_database()` creates tables automatically on app startup, but Alembic migration files also exist.
- Uploaded resumes are stored on disk, and the database stores the file path.
- LLM features are optional but better with `OPENROUTER_API_KEY`.
- Email features require EmailJS configuration.
- Resume processing is asynchronous, so Redis and Celery worker availability are required for real end-to-end ingestion.

## 11. One-Line Architecture

```text
Next.js ATS Portal -> Next.js API Proxy -> FastAPI -> SQLAlchemy -> PostgreSQL + pgvector
                                              |
                                              +-> Celery + Redis -> Resume parsing and embedding
                                              |
                                              +-> OpenRouter -> LLM enrichment, feedback, copilot answers
```

