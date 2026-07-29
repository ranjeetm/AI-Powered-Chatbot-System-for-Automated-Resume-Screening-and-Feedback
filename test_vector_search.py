from sentence_transformers import (
    SentenceTransformer
)

from backend.db.database import (
    SessionLocal
)

from backend.db.crud import (
    semantic_search
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

db = SessionLocal()

# --------------------------------
# JOB DESCRIPTION QUERY
# --------------------------------

job_description = """

Looking for a Python developer
with FastAPI, PostgreSQL,
machine learning, and NLP experience

"""

query_embedding = model.encode(
    job_description
)

results = semantic_search(
    db,
    query_embedding.tolist(),
    limit=10
)

print("\nTop Matching Candidates:\n")

for row in results:

    print(row)