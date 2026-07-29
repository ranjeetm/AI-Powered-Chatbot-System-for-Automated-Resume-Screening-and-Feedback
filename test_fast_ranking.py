from backend.ranking.fast_ranking_engine import (
    FastRankingEngine
)


engine = FastRankingEngine()


jd_text = """
Looking for a Data Scientist with:
- Python
- Machine Learning
- SQL
- NLP
- TensorFlow
- Tableau
"""


results = engine.rank_resumes(
    jd_text
)


print("\n" + "=" * 60)
print("FAST GLOBAL RANKING")
print("=" * 60)


for rank, result in enumerate(
    results[:20],
    start=1
):

    print(
        f"{rank}. "
        f"[{result['category']}] "
        f"{result['file_name']} "
        f"--> "
        f"{result['score']:.4f}"
    )