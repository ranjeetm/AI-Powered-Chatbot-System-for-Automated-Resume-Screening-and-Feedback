import json

from pathlib import Path

from backend.embeddings.embedding_engine import (
    EmbeddingEngine
)

from backend.scoring.weighted_scorer import (
    WeightedScorer
)


embedding_engine = EmbeddingEngine()

weighted_scorer = WeightedScorer()


jd_text = """
Looking for a Data Scientist with:
- Python
- Machine Learning
- SQL
- TensorFlow
- Tableau
"""


jd_embedding = (
    embedding_engine.generate_embedding(
        jd_text
    )
)


processed_dir = Path(
    "processed_resumes"
)


json_files = list(
    processed_dir.glob("*.json")
)


results = []


for json_file in json_files:

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        resume_data = json.load(f)

    semantic_similarity = (
        embedding_engine.calculate_similarity(
            resume_data["embedding"],
            jd_embedding
        )
    )

    skill_match = (
        weighted_scorer.calculate_skill_match(
            resume_data["text"],
            jd_text
        )
    )

    final_score = (
        weighted_scorer.calculate_final_score(
            semantic_similarity,
            skill_match
        )
    )

    results.append({

        "file_name":
            resume_data["file_name"],

        "category":
            resume_data["category"],

        "semantic_similarity":
            semantic_similarity,

        "skill_match":
            skill_match,

        "final_score":
            final_score
    })


results = sorted(
    results,
    key=lambda x: x["final_score"],
    reverse=True
)


print("\n" + "=" * 60)
print("WEIGHTED ATS RANKING")
print("=" * 60)


for rank, result in enumerate(
    results[:15],
    start=1
):

    print(
        f"\n{rank}. "
        f"[{result['category']}] "
        f"{result['file_name']}"
    )

    print(
        f"Semantic Similarity: "
        f"{result['semantic_similarity']:.4f}"
    )

    print(
        f"Skill Match: "
        f"{result['skill_match']:.4f}"
    )

    print(
        f"Final Score: "
        f"{result['final_score']:.4f}"
    )