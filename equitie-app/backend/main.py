from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .logging_config import logger
from .api.router import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API", environment=settings.environment)
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="EquiTie AI Portfolio Assistant API",
    description="Backend API for querying portfolio data.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
