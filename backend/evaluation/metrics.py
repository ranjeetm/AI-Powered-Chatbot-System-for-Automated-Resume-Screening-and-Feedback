class EvaluationMetrics:

    @staticmethod
    def precision_at_k(
        results,
        expected_categories,
        k=10
    ):

        top_k = results[:k]

        relevant = 0

        for result in top_k:

            if result["category"] in expected_categories:
                relevant += 1

        precision = relevant / k

        return precision

    @staticmethod
    def category_distribution(
        results,
        k=10
    ):

        top_k = results[:k]

        distribution = {}

        for result in top_k:

            category = result["category"]

            if category not in distribution:
                distribution[category] = 0

            distribution[category] += 1

        return distribution