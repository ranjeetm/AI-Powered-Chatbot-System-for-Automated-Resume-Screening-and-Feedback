from pathlib import Path

from backend.parser.parser import extract_text_from_pdf
from backend.embeddings.embedding_engine import EmbeddingEngine


engine = EmbeddingEngine()


# Sample Job Description
jd_text = """
Looking for a Data Scientist with:
- Python
- Machine Learning
- SQL
- NLP
- TensorFlow
- Deep Learning
"""


# Generate JD Embedding
jd_embedding = engine.generate_embedding(
    jd_text
)


resume_dir = Path(
    "datasets/resumes/data_science"
)

results = []


for pdf_file in resume_dir.glob("*.pdf"):

    parsed = extract_text_from_pdf(pdf_file)

    resume_text = parsed["text"]

    resume_embedding = engine.generate_embedding(
        resume_text
    )

    similarity = engine.calculate_similarity(
        resume_embedding,
        jd_embedding
    )

    results.append(
        (
            pdf_file.name,
            similarity
        )
    )


# Sort By Similarity
results = sorted(
    results,
    key=lambda x: x[1],
    reverse=True
)


print("\nTOP MATCHES:\n")


for file_name, score in results:

    print(
        f"{file_name} --> {score:.4f}"
    )