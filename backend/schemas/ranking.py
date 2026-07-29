from pydantic import BaseModel
from typing import Optional, List

# --------------------------------
# REQUEST
# --------------------------------


class RankingRequest(BaseModel):

    job_description: str

    top_k: int = 5


# --------------------------------
# RESPONSE ITEM
# --------------------------------


class RankedCandidateResponse(BaseModel):

    id: int

    candidate_name: Optional[str] = None

    semantic_score: Optional[float] = None

    weighted_score: Optional[float] = None

    recruiter_score: Optional[float] = None

    distance: Optional[float] = None

    class Config:
        from_attributes = True


# --------------------------------
# FULL RESPONSE
# --------------------------------


class RankingResponse(BaseModel):

    ranked_candidates: List[dict]
