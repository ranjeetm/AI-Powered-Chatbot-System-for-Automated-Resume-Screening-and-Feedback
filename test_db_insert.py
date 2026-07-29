from backend.db.database import SessionLocal
from backend.db.crud import insert_candidate

db = SessionLocal()

sample_profile = {

    "file_name": "resume.pdf",

    "candidate_name": "Ranjeet",

    "email": "ranjeet@test.com",

    "skills": ["Python", "FastAPI", "PostgreSQL"],

    "experience_years": 2,

    "resume_text": "Sample resume text",

    "cleaned_text": "sample cleaned text",

    "semantic_score": 0.91,

    "weighted_score": 88.5,

    "recruiter_score": 90.0
}

dummy_embedding = [0.1] * 384

candidate = insert_candidate(
    db,
    sample_profile,
    dummy_embedding
)

print(candidate.id)