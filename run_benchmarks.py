from backend.evaluation.benchmark_runner import (
    BenchmarkRunner
)


runner = BenchmarkRunner()


benchmark_cases = [

    {
        "name": "Data Scientist Benchmark",

        "job_description": """
        Looking for a Data Scientist with:
        - Python
        - Machine Learning
        - SQL
        - NLP
        - TensorFlow
        - Tableau
        """,

        "expected_categories": [
            "data_science",
            "python_developer"
        ]
    },

    {
        "name": "DevOps Engineer Benchmark",

        "job_description": """
        Looking for a DevOps Engineer with:
        - Docker
        - Kubernetes
        - AWS
        - CI/CD
        - Linux
        - Terraform
        """,

        "expected_categories": [
            "devops"
        ]
    },

    {
        "name": "HR Specialist Benchmark",

        "job_description": """
        Looking for an HR Specialist with:
        - Recruitment
        - Talent Acquisition
        - Employee Relations
        - HR Policies
        - Communication Skills
        """,

        "expected_categories": [
            "hr"
        ]
    }
]


runner.run_benchmark(
    benchmark_cases,
    k=10
)