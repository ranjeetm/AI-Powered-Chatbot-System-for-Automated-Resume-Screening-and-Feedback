from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRetrievalFilters(BaseModel):
    candidate_ids: Optional[list[int]] = None
    skills: Optional[list[str]] = None
    category: Optional[str] = None
    location: Optional[str] = None
    min_experience_years: Optional[int] = Field(default=None, ge=0)
    job_id: Optional[int] = None


class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=12000)
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: int = Field(default=6, ge=1, le=12)
    filters: ChatRetrievalFilters = Field(default_factory=ChatRetrievalFilters)
    stream: bool = False


class RelevantSection(BaseModel):
    name: str
    snippet: str
    full_text: Optional[str] = None


class CandidateEvidence(BaseModel):
    candidate_id: int
    candidate_name: Optional[str] = None
    category: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    recruiter_score: Optional[float] = None
    semantic_similarity: float = 0.0
    keyword_score: float = 0.0
    hybrid_score: float = 0.0
    final_score: float = 0.0
    matching_reasons: list[str] = Field(default_factory=list)
    relevant_sections: list[RelevantSection] = Field(default_factory=list)
    project_highlights: list[str] = Field(default_factory=list)
    experience_highlights: list[str] = Field(default_factory=list)


class RetrievalDiagnostics(BaseModel):
    retrieval_count: int
    model: str
    intent: str
    filters_applied: dict[str, Any] = Field(default_factory=dict)


class CopilotChatResponse(BaseModel):
    answer: str
    candidates: list[CandidateEvidence] = Field(default_factory=list)
    diagnostics: RetrievalDiagnostics
