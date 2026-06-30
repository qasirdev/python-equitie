from typing import Any, List

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..agent.runner import run_agent_loop
from ..data_layer.loader import data_store
from ..security.gate import PromptInjectionDetector

logger = structlog.get_logger("equitie_backend.api")

router = APIRouter()


class ChatRequest(BaseModel):
    investor_id: str
    messages: List[Any]


@router.get("/health")
def health_check() -> dict[str, str]:
    logger.info("Health check endpoint called", trace_id="system")
    return {"status": "ok"}


@router.get("/investors")
def get_investors() -> list[dict[str, Any]]:
    investors = data_store.investors
    if investors.empty:
        return []
    return investors[["investor_id", "investor_name"]].to_dict(orient="records")  # type: ignore[return-value]


@router.post("/chat")
async def chat_endpoint(req: ChatRequest) -> StreamingResponse:
    # Basic security check on the latest user message
    latest_msg = next(
        (m for m in reversed(req.messages) if m.get("role") == "user"), None
    )
    if latest_msg and latest_msg.get("content"):
        PromptInjectionDetector.check_query(latest_msg["content"])

    # Run agent loop and return streaming response
    return StreamingResponse(
        run_agent_loop(req.investor_id, req.messages), media_type="text/event-stream"
    )
