# AI Resume Screening ATS Documentation

## 1. Project Overview

This project is an AI-powered Applicant Tracking System (ATS) for resume intake, parsing, semantic ranking, recruiter workflows, candidate applications, and an AI Recruiter Copilot chatbot.

The system supports two primary users:

- **Candidates**: browse jobs and submit resume applications.
- **Recruiters**: authenticate, upload resumes, create jobs, rank candidates, view analytics, inspect candidate profiles, download resumes, and ask an AI copilot recruiter-focused questions.

The platform is not a generic resume uploader. It combines OCR/text extraction, structured resume parsing, embeddings, pgvector search, recruiter scoring, job matching, and OpenRouter LLM responses.

## 2. Core Capabilities

- JWT-based recruiter authentication
- Candidate job browsing and resume application submission
- Recruiter resume intake
- PDF text extraction and OCR-ready parsing pipeline
- Structured resume extraction:
  - candidate name
  - email
  - phone
  - location
  - links
  - skills
  - job titles
  - education
  - degrees
  - projects
  - experience
  - resume sections
- SentenceTransformers resume embeddings
- PostgreSQL + pgvector vector storage
- Semantic candidate search
- Candidate ranking against job descriptions
- Redis + Celery asynchronous resume processing
- OpenRouter LLM enrichment
- AI Recruiter Copilot chatbot using RAG
- Recruiter-friendly frontend UI in Next.js

## 3. Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Redis
- Celery
- SentenceTransformers
- spaCy
- PyMuPDF / pdfplumber / OCR-related PDF tooling
- OpenRouter API
- JWT authentication with `python-jose`
- Password hashing with Passlib and bcrypt

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Local Next.js API proxy for backend forwarding

### Infrastructure

- Docker Compose
- PostgreSQL with pgvector image
- Redis/Celery-compatible async processing

## 4. Requirements

### System Requirements

- Python 3.11+ or 3.12+
- Node.js 20+
- PostgreSQL with pgvector extension
- Redis for Celery queue
- Tesseract/poppler tooling if OCR processing is required by your environment
- OpenRouter API key for LLM features

### Python Requirements

The main dependencies are listed in `requirements.txt`.

Important packages include:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg2-binary`
- `pgvector`
- `sentence-transformers`
- `spacy`
- `PyMuPDF`
- `pdfplumber`
- `pytesseract`
- `openai`
- `httpx`
- `redis`
- `celery`
- `python-jose[cryptography]`
- `passlib[bcrypt]`

### Frontend Requirements

The frontend dependencies are listed in `frontend/package.json`.

Main packages:

- `next`
- `react`
- `react-dom`
- `typescript`
- `tailwindcss`

## 5. Environment Variables

Create a backend `.env` or root `.env` depending on how you run the app.

Required:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
OPENROUTER_API_KEY=your_openrouter_api_key
```

Optional:

```env
LOCAL_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ats_db
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_CHAT_MODEL=openai/gpt-4o-mini
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_FALLBACK_MODELS=openai/gpt-oss-20b:free,z-ai/glm-4.5-air:free,openrouter/free
OPENROUTER_TIMEOUT_SECONDS=45
OPENROUTER_APP_TITLE=AI Resume Screening ATS
OPENROUTER_HTTP_REFERER=http://localhost:3000
RESUME_UPLOAD_DIR=/tmp/resume_project_uploads
EMAILJS_SERVICE_ID=your_emailjs_service_id
EMAILJS_TEMPLATE_ID=your_emailjs_template_id
EMAILJS_PUBLIC_KEY=your_emailjs_public_key
EMAILJS_PRIVATE_KEY=your_emailjs_private_key_optional
EMAILJS_API_URL=https://api.emailjs.com/api/v1.0/email/send
EMAILJS_TIMEOUT_SECONDS=5
```

`EMAILJS_SERVICE_ID`, `EMAILJS_TEMPLATE_ID`, and `EMAILJS_PUBLIC_KEY` are required for candidate shortlist/unshortlist notification emails and JD match recruiter summary emails.

Frontend `.env.local`:

```env
BACKEND_API_URL=http://127.0.0.1:8000
```

Never commit real API keys to source control.

## 6. High-Level Architecture

```text
Candidate / Recruiter UI
        |
        v
Next.js Frontend
        |
        v
Next.js API Proxy (/api/backend/*)
        |
        v
FastAPI Backend
        |
        +--> JWT Auth
        +--> Resume Upload / Candidate Apply
        +--> Job Posting APIs
        +--> Candidate Detail APIs
        +--> Ranking APIs
        +--> Recruiter Copilot APIs
        |
        v
PostgreSQL + pgvector
        |
        v
Candidate Profiles, Resume Text, Structured Fields, Embeddings, Scores

Resume processing:

PDF Upload
   -> Celery Task
   -> PDF Text/OCR Extraction
   -> Structured Parser
   -> SentenceTransformer Embedding
   -> OpenRouter Enrichment
   -> PostgreSQL Insert

Recruiter Copilot:

Recruiter Query
   -> Query Embedding
   -> pgvector Search
   -> Keyword Search
   -> Metadata Filters
   -> Recruiter Score Boost
   -> Reranking
   -> Structured Context Builder
   -> OpenRouter LLM
   -> Answer + Candidate Evidence Cards
```

## 7. Backend Folder Structure

```text
backend/
  api/
    main.py
    auth.py
    routes/
      upload.py
      candidates.py
      jobs.py
      ranking.py
      chatbot.py

  core/
    security.py
    celery_app.py

  db/
    database.py
    session.py
    models.py
    auth_models.py
    initializer.py
    crud.py

  repositories/
    auth_repository.py
    candidate_repository.py
    chatbot_repository.py

  schemas/
    auth.py
    candidate.py
    job.py
    ranking.py
    upload.py
    chatbot.py

  services/
    auth_service.py
    candidate_ranking_service.py
    resume_ingestion_service.py
    llm_enrichment.py
    chatbot/
      copilot_service.py
      retrieval_service.py
      reranking_service.py
      context_builder.py
      openrouter_client.py
      response_formatter.py

  parser/
    parser.py

  extraction/
    structured_parser.py
    section_parser.py
    skill_extractor.py
    experience_extractor.py
    education_extractor.py

  embeddings/
    embedding_engine.py

  scoring/
    profile_scorer.py
    weighted_scorer.py

  tasks/
    resume_tasks.py
```

## 8. Frontend Folder Structure

```text
frontend/
  app/
    page.tsx
    layout.tsx
    globals.css
    api/
      backend/
        [...path]/
          route.ts

  components/
    ats/
      AtsPortal.tsx
      ui.tsx

  lib/
    api.ts

  package.json
  next.config.ts
```

## 9. Database Models

### CandidateProfile

Stored in `candidate_profiles`.

Important fields:

- `id`
- `file_name`
- `candidate_name`
- `email`
- `phone`
- `location`
- `linkedin_url`
- `github_url`
- `category`
- `skills`
- `job_titles`
- `degrees`
- `specializations`
- `certifications`
- `education`
- `projects`
- `experience`
- `sections`
- `experience_years`
- `resume_summary`
- `resume_text`
- `cleaned_text`
- `resume_file_path`
- `semantic_score`
- `weighted_score`
- `recruiter_score`
- `embedding Vector(384)`
- `parsed_at`

### JobPosting

Stored in `job_postings`.

Fields:

- `id`
- `title`
- `department`
- `location`
- `type`
- `description`
- `skills`
- `created_at`

## 10. Application Startup

FastAPI starts in `backend/api/main.py`.

Startup behavior:

1. Loads database configuration.
2. Initializes pgvector extension.
3. Creates database tables from SQLAlchemy models.
4. Applies compatibility fixes for newer columns.
5. Registers API routes.
6. Enables CORS for local frontend ports.

Main included routers:

- upload routes
- ranking routes
- candidate routes
- job routes
- recruiter copilot routes
- auth routes

## 11. Authentication Flow

### Register

Endpoint:

```http
POST /register
```

Flow:

1. Recruiter submits full name, email, and password.
2. Backend hashes password.
3. User is stored in the users table.
4. Backend returns user ID.

### Login

Endpoint:

```http
POST /login
```

Flow:

1. Recruiter submits email and password as OAuth2 form data.
2. Backend verifies password.
3. Backend creates JWT access token.
4. Frontend stores token in `localStorage`.
5. Protected requests include `Authorization: Bearer <token>`.

Protected endpoints use `get_current_user`.

## 12. Resume Upload and Processing Flow

### Recruiter Upload

Endpoint:

```http
POST /upload-resume
```

Requires JWT authentication.

Flow:

1. Recruiter uploads a PDF resume.
2. Backend validates the file extension.
3. PDF is saved to `RESUME_UPLOAD_DIR`.
4. Backend queues `process_resume_task` in Celery.
5. API responds immediately with a queued status.

### Candidate Application

Endpoint:

```http
POST /candidate-apply
```

Flow:

1. Candidate selects a job.
2. Candidate submits name, email, job ID, and resume PDF.
3. Backend validates job exists.
4. Resume is saved with a generated prefix.
5. Celery queues resume processing.
6. Candidate metadata overrides are passed into the ingestion task.

### Celery Processing

Task:

```text
backend.tasks.resume_tasks.process_resume_task
```

Flow:

1. Initialize database.
2. Create `ResumeIngestionService`.
3. Extract text from PDF.
4. Generate resume embedding.
5. Build structured candidate profile.
6. Apply candidate metadata overrides if present.
7. Enrich resume with OpenRouter LLM.
8. Merge parser skills and LLM skills.
9. Store resume text, summary, file path, scores, and embedding.
10. Insert candidate into PostgreSQL.

## 13. Resume Parsing Flow

```text
PDF file
  -> extract_text_from_pdf
  -> raw resume text
  -> StructuredResumeParser
  -> sections, skills, education, projects, experience
  -> LLM enrichment
  -> final candidate profile
```

The system keeps both raw text and structured data. This is important because:

- raw text supports fallback keyword search
- structured fields support recruiter-facing explanations
- sections support RAG evidence
- embeddings support semantic search

## 14. Embedding Flow

The project uses SentenceTransformers with `all-MiniLM-L6-v2`.

Resume embedding flow:

```text
resume text
  -> SentenceTransformer.encode
  -> 384-dimensional vector
  -> candidate_profiles.embedding
```

Query embedding flow:

```text
job description or recruiter query
  -> SentenceTransformer.encode
  -> 384-dimensional vector
  -> pgvector similarity search
```

## 15. Candidate Ranking Flow

Endpoint:

```http
POST /rank-candidates
```

Requires JWT authentication.

Input:

```json
{
  "job_description": "string",
  "top_k": 10
}
```

Flow:

1. Generate embedding for the job description.
2. Run pgvector semantic search.
3. Fetch candidate profiles.
4. Calculate:
   - semantic similarity
   - skill match
   - title match
   - experience match
5. Calculate final score.
6. Sort candidates by score.
7. Return ranked candidate cards.

Scoring weights:

- semantic similarity: 50%
- skill match: 30%
- title match: 10%
- experience match: 10%

## 16. AI Recruiter Copilot

The Recruiter Copilot is a recruiter-focused RAG chatbot. It is not a generic chatbot.

It can answer:

- “Find backend developers with FastAPI and Docker”
- “Who has the strongest NLP background?”
- “Summarize the top 3 candidates”
- “Why is candidate A ranked higher?”
- “Which candidates match this JD?”
- “Who lacks Kubernetes experience?”
- “Explain shortlist reasoning”

### Copilot API Endpoints

Standard response:

```http
POST /recruiter-copilot/chat
```

Streaming response:

```http
POST /recruiter-copilot/chat/stream
```

Both require JWT authentication.

### Copilot Request

```json
{
  "message": "Find backend developers with FastAPI and Docker",
  "history": [
    {
      "role": "user",
      "content": "Previous question"
    }
  ],
  "top_k": 6,
  "filters": {
    "skills": ["FastAPI", "Docker"],
    "category": "backend",
    "min_experience_years": 2,
    "candidate_ids": [1, 2, 3],
    "job_id": 5
  },
  "stream": true
}
```

### Copilot Response

```json
{
  "answer": "Recruiter-focused answer...",
  "candidates": [
    {
      "candidate_id": 1,
      "candidate_name": "Candidate Name",
      "skills": ["Python", "FastAPI"],
      "matched_skills": ["FastAPI"],
      "missing_skills": ["Docker"],
      "semantic_similarity": 0.82,
      "keyword_score": 0.44,
      "hybrid_score": 0.76,
      "final_score": 0.79,
      "matching_reasons": [],
      "relevant_sections": []
    }
  ],
  "diagnostics": {
    "retrieval_count": 6,
    "model": "openai/gpt-4o-mini",
    "intent": "semantic_candidate_search",
    "filters_applied": {}
  }
}
```

## 17. Copilot RAG Flow

```text
Recruiter Query
  -> Detect intent
  -> Optional job context lookup
  -> Extract query skills
  -> Generate query embedding
  -> Hybrid retrieval
       - pgvector semantic similarity
       - PostgreSQL full-text keyword rank
       - metadata filtering
       - recruiter score boost
  -> Reranking
       - semantic score
       - keyword score
       - recruiter score
       - matched skills
       - relevant resume sections
       - experience signal
  -> Build structured context
  -> OpenRouter LLM
  -> Format recruiter answer
  -> Return answer + evidence cards
```

### Intent Detection

The copilot detects broad recruiter intents:

- `candidate_comparison`
- `resume_summarization`
- `missing_skill_analysis`
- `jd_matching`
- `ranking_explanation`
- `shortlist_recommendation`
- `semantic_candidate_search`

### Hybrid Retrieval

Implemented in `backend/repositories/chatbot_repository.py`.

Signals:

- `embedding <=> CAST(:embedding AS vector)` for vector distance
- `GREATEST(0, 1 - distance)` for semantic similarity
- `ts_rank_cd` over candidate text and structured fields for keyword matching
- metadata filters for candidate IDs, category, location, skills, and experience
- recruiter score boost from `candidate_profiles.recruiter_score`

### Reranking

Implemented in `backend/services/chatbot/reranking_service.py`.

Signals:

- semantic similarity
- keyword score
- recruiter score boost
- skill match ratio
- relevant section count
- experience score

The reranker also builds evidence:

- matched skills
- missing skills
- matching reasons
- relevant resume sections
- project highlights
- experience highlights

### Context Building

Implemented in `backend/services/chatbot/context_builder.py`.

The system does not send raw resume chunks directly to the LLM.

It builds structured recruiter-friendly dossiers:

```text
Candidate Name
Category
Experience Years
Recruiter Score
Final RAG Score
Semantic Similarity
Keyword Score
Skills
Matched Skills
Missing Skills
Matching Reasons
Relevant Resume Sections
Experience Highlights
Project Highlights
```

### OpenRouter Integration

Implemented in `backend/services/chatbot/openrouter_client.py`.

Uses:

```text
https://openrouter.ai/api/v1/chat/completions
```

Supports:

- normal chat completion
- streaming chat completion
- model configuration through environment variables
- OpenRouter headers:
  - `Authorization`
  - `HTTP-Referer`
  - `X-Title`

### Copilot Streaming

Streaming endpoint returns server-sent events:

```text
data: {"type":"metadata", ...}
data: {"type":"token","content":"..."}
data: {"type":"done"}
```

Frontend consumes this stream and updates the assistant message incrementally.

## 18. Frontend Application Flow

The main frontend entry point is `frontend/components/ats/AtsPortal.tsx`.

### Landing

Users choose:

- Candidate Portal
- Recruiter Portal

### Candidate Portal

Tabs:

- Browse Jobs
- Apply

Candidate flow:

```text
Browse jobs
  -> select role
  -> upload resume
  -> submit application
  -> backend queues resume processing
```

### Recruiter Portal

Tabs:

- AI Copilot
- Rank Candidates
- Job Postings
- Resume Intake
- Analytics

Recruiter flow:

```text
Login/Register
  -> access protected recruiter portal
  -> upload resumes
  -> create jobs
  -> rank candidates
  -> inspect candidate details
  -> ask copilot questions
  -> review evidence cards
```

## 19. Frontend API Layer

Implemented in `frontend/lib/api.ts`.

Main API helpers:

- `loginUser`
- `registerUser`
- `rankCandidates`
- `uploadResume`
- `submitCandidateApplication`
- `getJobs`
- `createJob`
- `getCandidate`
- `getCandidateResumeUrl`
- `sendRecruiterCopilotMessage`
- `streamRecruiterCopilotMessage`

The frontend stores JWT token in `localStorage` and sends it through the `Authorization` header.

## 20. Next.js Backend Proxy

Implemented in:

```text
frontend/app/api/backend/[...path]/route.ts
```

Purpose:

- avoids direct browser/backend CORS issues
- forwards authorization headers
- supports file and JSON requests
- forwards streaming response bodies
- tries common local backend ports

Frontend calls:

```text
/api/backend/*
```

Proxy forwards to:

```text
http://127.0.0.1:8000
```

or other configured backend URLs.

## 21. API Endpoint Summary

### Auth

```http
POST /register
POST /login
```

### Jobs

```http
GET /jobs
POST /jobs
```

### Resume Upload

```http
POST /upload-resume
POST /candidate-apply
```

### Candidates

```http
GET /candidate/{candidate_id}
GET /candidate-resume/{candidate_id}
POST /candidates/{candidate_id}/shortlist
POST /candidates/{candidate_id}/unshortlist
```

`GET /candidate/{candidate_id}` may include optional `is_shortlisted`, `shortlist_updated_at`, and `rejection_feedback` fields when present.

Shortlist/unshortlist endpoints require recruiter JWT. They update candidate shortlist status and send candidate notification emails via EmailJS when configured.

Example:

```http
POST /candidates/12/shortlist
Authorization: Bearer <token>
Content-Type: application/json

{ "job_title": "Junior ML Engineer" }
```

```http
POST /candidates/12/unshortlist
Authorization: Bearer <token>
Content-Type: application/json

{ "feedback": "We are moving forward with candidates whose production ML experience is stronger.", "job_title": "Junior ML Engineer" }
```

Response:

```json
{
  "message": "Candidate shortlisted and notification email sent.",
  "is_shortlisted": true,
  "email_sent": true
}
```

### Ranking

```http
POST /rank-candidates
```

### Recruiter Copilot

```http
POST /recruiter-copilot/chat
POST /recruiter-copilot/chat/stream
```

## 22. Running Locally

### Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI:

```bash
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

### Celery Worker

Run a worker with the configured Celery app:

```bash
celery -A backend.core.celery_app.celery_app worker --loglevel=info
```

Redis must be running before Celery can process tasks.

### Docker Compose

```bash
docker compose up --build
```

Default container ports:

- PostgreSQL: host `5433` -> container `5432`
- Backend: host `8001` -> container `8000`
- Frontend: host `3001` -> container `3000`

## 23. Testing and Verification

Useful commands:

```bash
python -m compileall backend
```

```bash
cd frontend
npm run build
```

Existing test files include:

- `test_embeddings.py`
- `test_vector_search.py`
- `test_candidate_ranking.py`
- `test_ranking_engine.py`
- `test_profile_scoring.py`
- `test_structured_parser.py`
- `test_skill_extraction.py`
- `test_experience_extraction.py`
- `test_metrics.py`

Run tests:

```bash
pytest
```

## 24. Common Workflows

### Add a New Resume

```text
Recruiter login
  -> Resume Intake
  -> Upload PDF
  -> Celery processes resume
  -> Candidate profile inserted
  -> Candidate appears in ranking and copilot retrieval
```

### Add a Job

```text
Recruiter login
  -> Job Postings
  -> Post New Job
  -> Candidate portal displays role
  -> Candidates can apply
```

### Rank Candidates

```text
Recruiter login
  -> Rank Candidates
  -> Paste job description
  -> Backend ranks using embeddings and profile scoring
  -> Candidate cards and analytics update
```

### Ask the AI Copilot

```text
Recruiter login
  -> AI Copilot
  -> Ask recruiter-focused question
  -> System retrieves candidate evidence
  -> OpenRouter generates answer
  -> UI displays answer and candidate evidence cards
```

## 25. Troubleshooting

### Backend Cannot Start

Check:

- `DATABASE_URL`
- PostgreSQL is running
- pgvector extension is available
- dependencies are installed
- SentenceTransformer model can be downloaded or is cached

### Resume Upload Queues but Does Not Process

Check:

- Redis is running
- Celery worker is running
- `backend.core.celery_app` configuration
- worker logs for PDF/OCR errors

### Copilot Returns Fallback Answer

Check:

- `OPENROUTER_API_KEY`
- network access to OpenRouter
- selected `OPENROUTER_CHAT_MODEL`
- candidate data exists in database
- embeddings exist in `candidate_profiles.embedding`

### No Candidate Matches

Check:

- resumes have been processed
- embeddings are not null
- filters are not too restrictive
- query skills match extracted skills
- candidate categories and experience fields are populated

### Frontend Cannot Reach Backend

Check:

- backend is running on port `8000`
- `frontend/.env.local` has correct `BACKEND_API_URL`
- Next.js proxy route is available
- browser has a valid JWT token for protected recruiter routes

## 26. Production Notes

Before production deployment:

- replace hardcoded JWT secret with environment-based secret
- use strong database credentials
- use HTTPS
- configure proper CORS origins
- secure uploaded resume storage
- add file size limits and malware scanning
- add structured logging
- add monitoring for Celery tasks
- add rate limiting on auth and copilot endpoints
- use persistent Redis/PostgreSQL services
- add database migrations for schema changes
- avoid storing raw secrets in `.env` committed to git
- add background cleanup for temporary upload files if required

## 27. Security Notes

Current recruiter routes are protected with JWT.

Sensitive areas:

- resume PDFs contain personal data
- raw resume text contains personal data
- candidate emails and phone numbers are stored
- OpenRouter receives structured candidate context during copilot requests

Recommended safeguards:

- restrict recruiter access by role
- audit copilot queries
- redact fields where possible
- encrypt storage where required
- define resume retention policies
- ensure LLM provider usage complies with privacy requirements

## 28. Key Design Decisions

- Use pgvector because resume matching is semantic, not only keyword-based.
- Keep structured resume fields so recruiter explanations are transparent.
- Use Celery because PDF parsing, embedding, OCR, and LLM enrichment are slow.
- Use OpenRouter for flexible LLM model selection.
- Return candidate evidence separately from the LLM answer so the UI can show grounded proof.
- Do not send raw resume chunks directly to the copilot. Build structured recruiter context first.
- Keep the frontend as a single ATS portal component for simple local development and demonstration.

## 29. Future Improvements

- Add persistent chat history table
- Add organization/team multi-tenancy
- Add role-based access control
- Add candidate notes and recruiter feedback
- Add interview scheduling
- Add ranking audit logs
- Add job-specific candidate shortlist table
- Add vector indexes for large-scale retrieval
- Add Redis caching for repeated copilot retrieval
- Add reranker model for stronger candidate ordering
- Add streaming markdown renderer
- Add attachments and JD upload support for copilot
- Add feedback buttons to improve ranking quality
