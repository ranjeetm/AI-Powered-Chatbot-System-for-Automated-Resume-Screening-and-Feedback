import json

from pathlib import Path

from backend.embeddings.embedding_engine import (
    EmbeddingEngine
)

from backend.scoring.profile_scorer import (
    ProfileScorer
)

from backend.extraction.structured_parser import (
    StructuredResumeParser
)


embedding_engine = EmbeddingEngine()

profile_scorer = ProfileScorer()

structured_parser = StructuredResumeParser()


jd_text = """
Looking for a Data Scientist with:
- Python
- Machine Learning
- SQL
- TensorFlow
- Tableau

Role:
Data Scientist

Required Experience:
2 years
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

    candidate_profile = (
        structured_parser.build_candidate_profile(
            resume_data
        )
    )

    semantic_similarity = (
        embedding_engine.calculate_similarity(
            candidate_profile["embedding"],
            jd_embedding
        )
    )

    skill_match = (
        profile_scorer.calculate_skill_match(
            candidate_profile["skills"],
            jd_text
        )
    )

    title_match = (
        profile_scorer.calculate_title_match(
            candidate_profile["job_titles"],
            jd_text
        )
    )

    experience_match = (
        profile_scorer.calculate_experience_match(
            candidate_profile["experience_years"],
            required_experience=2
        )
    )

    final_score = (
        profile_scorer.calculate_final_score(
            semantic_similarity,
            skill_match,
            title_match,
            experience_match
        )
    )

    results.append({

        "file_name":
            candidate_profile["file_name"],

        "category":
            candidate_profile["category"],

        "semantic_similarity":
            semantic_similarity,

        "skill_match":
            skill_match,

        "title_match":
            title_match,

        "experience_match":
            experience_match,

        "final_score":
            final_score
    })


results = sorted(
    results,
    key=lambda x: x["final_score"],
    reverse=True
)


print("\n" + "=" * 60)
print("PROFILE-BASED ATS RANKING")
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
        f"Title Match: "
        f"{result['title_match']:.4f}"
    )

    print(
        f"Experience Match: "
        f"{result['experience_match']:.4f}"
    )

    print(
        f"FINAL SCORE: "
        f"{result['final_score']:.4f}"
    )