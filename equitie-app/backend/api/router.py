from fastapi import APIRouter
import structlog

logger = structlog.get_logger("equitie_backend.api")

router = APIRouter()


@router.get("/health")
def health_check():
    logger.info("Health check endpoint called", trace_id="system")
    return {"status": "ok"}
