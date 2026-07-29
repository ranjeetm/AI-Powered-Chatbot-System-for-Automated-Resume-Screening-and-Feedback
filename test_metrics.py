from backend.ranking.ranking_engine import RankingEngine
from backend.evaluation.metrics import EvaluationMetrics


engine = RankingEngine()


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


expected_categories = [
    "data_science",
    "python_developer"
]


precision = (
    EvaluationMetrics.precision_at_k(
        results,
        expected_categories,
        k=10
    )
)


distribution = (
    EvaluationMetrics.category_distribution(
        results,
        k=10
    )
)


print("\n" + "=" * 60)
print("EVALUATION RESULTS")
print("=" * 60)

print(
    f"\nPrecision@10: {precision:.2f}"
)

print("\nCategory Distribution:")

for category, count in distribution.items():

    print(
        f"{category}: {count}"
    )