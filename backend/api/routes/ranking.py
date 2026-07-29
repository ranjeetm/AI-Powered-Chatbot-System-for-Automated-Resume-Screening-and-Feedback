from fastapi import (
    APIRouter,
    Depends
)

from backend.services.candidate_ranking_service import (
    CandidateRankingService
)

from backend.schemas.ranking import (
    RankingRequest,
    RankingResponse
)

from backend.core.security import (
    get_current_user
)


router = APIRouter()


service = CandidateRankingService()


@router.post(
    "/rank-candidates",
    response_model=RankingResponse
)

def rank_candidates(

    payload: RankingRequest,

    current_user = Depends(
        get_current_user
    )
):

    results = service.rank_candidates(

        payload.job_description,

        payload.top_k
    )

    return {

        "ranked_candidates":
            results
    }