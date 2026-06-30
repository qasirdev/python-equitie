from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import router as api_router
from .logging_config import logger
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled Exception", exc_info=exc, path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
