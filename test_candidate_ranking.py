from backend.services.candidate_ranking_service import (
    CandidateRankingService
)


service = CandidateRankingService()


job_description = """

Looking for a Python developer
with FastAPI, PostgreSQL,
Docker, SQL, and AWS experience.

Must have experience building
machine learning systems.

"""


results = service.rank_candidates(
    job_description,
    top_k=5
)


print("\nTOP RANKED CANDIDATES:\n")


for candidate in results:

    print(candidate)

    print("-" * 50)