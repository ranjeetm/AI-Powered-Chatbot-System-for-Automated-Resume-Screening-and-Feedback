from backend.ranking.fast_ranking_engine import (
    FastRankingEngine
)

from backend.evaluation.metrics import (
    EvaluationMetrics
)


class BenchmarkRunner:

    def __init__(self):

        self.ranking_engine = (
            FastRankingEngine()
        )

    def run_benchmark(
        self,
        benchmark_cases,
        k=10
    ):

        benchmark_results = []

        for benchmark in benchmark_cases:

            print("\n" + "=" * 60)

            print(
                f"RUNNING BENCHMARK: "
                f"{benchmark['name']}"
            )

            results = (
                self.ranking_engine.rank_resumes(
                    benchmark["job_description"]
                )
            )

            precision = (
                EvaluationMetrics.precision_at_k(
                    results,
                    benchmark["expected_categories"],
                    k=k
                )
            )

            distribution = (
                EvaluationMetrics.category_distribution(
                    results,
                    k=k
                )
            )

            benchmark_results.append({

                "benchmark_name":
                    benchmark["name"],

                "precision_at_k":
                    precision,

                "distribution":
                    distribution
            })

            print(
                f"\nPrecision@{k}: "
                f"{precision:.2f}"
            )

            print("\nCategory Distribution:")

            for category, count in distribution.items():

                print(
                    f"{category}: {count}"
                )

        return benchmark_results