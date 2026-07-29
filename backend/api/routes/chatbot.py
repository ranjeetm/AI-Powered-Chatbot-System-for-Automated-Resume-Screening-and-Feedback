from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.schemas.chatbot import (
    CopilotChatRequest,
    CopilotChatResponse,
    RetrievalDiagnostics,
)
from backend.services.chatbot.copilot_service import RecruiterCopilotService


router = APIRouter(
    prefix="/recruiter-copilot",
    tags=["recruiter-copilot"],
)

service = RecruiterCopilotService()


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
)
async def recruiter_copilot_chat(
    payload: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    answer, candidates, intent, model = await service.answer(
        db=db,
        message=payload.message,
        history=payload.history,
        top_k=payload.top_k,
        filters=payload.filters,
    )

    return CopilotChatResponse(
        answer=answer,
        candidates=candidates,
        diagnostics=RetrievalDiagnostics(
            retrieval_count=len(candidates),
            model=model,
            intent=intent,
            filters_applied=payload.filters.model_dump(exclude_none=True),
        ),
    )


@router.post("/chat/stream")
async def recruiter_copilot_chat_stream(
    payload: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return StreamingResponse(
        service.stream_answer(
            db=db,
            message=payload.message,
            history=payload.history,
            top_k=payload.top_k,
            filters=payload.filters,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
