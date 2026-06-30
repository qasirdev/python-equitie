from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .logging_config import logger

app = FastAPI(
    title="EquiTie AI Portfolio Assistant API",
    description="Backend API for querying portfolio data.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting API in {settings.environment} mode.")


@app.get("/health")
def health_check():
    return {"status": "ok"}
