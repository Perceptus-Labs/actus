"""
Main FastAPI application for V-JEPA-2 deployment.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api import router
from src.api.routes import load_models

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting V-JEPA-2 API server...")
    try:
        load_models()
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        logger.warning("Server will start but models may not be available")

    yield

    # Shutdown
    logger.info("Shutting down V-JEPA-2 API server...")


# Create FastAPI app
app = FastAPI(
    title="V-JEPA-2 API",
    description="API for visual intention analysis using V-JEPA-2 model",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": "2024-01-01T12:00:00Z",
        },
    )


# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "V-JEPA-2 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
