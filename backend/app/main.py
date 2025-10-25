"""Main FastAPI application."""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.inference import inference_engine
from app.api.routes import generation, models, embeddings
from app.api.middleware.metrics import MetricsMiddleware, get_metrics

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load model on startup, cleanup on shutdown."""
    # Startup
    logger.info("Starting AI UA API server")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Context size: {settings.model_context_size}")
    logger.info(f"Max concurrent requests: {settings.max_concurrent_requests}")

    try:
        inference_engine.load_model()
        logger.info("Model loaded successfully - server ready")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.error("Server starting without model - health check will fail")

    yield

    # Shutdown
    logger.info("Shutting down server")
    inference_engine.shutdown()


# Create FastAPI app
app = FastAPI(
    title="AI UA - Local Gemini-compatible API",
    description="Ukrainian AI model with Gemini-compatible API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
if settings.enable_metrics:
    app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(generation.router, prefix="/v1", tags=["generation"])
app.include_router(models.router, prefix="/v1", tags=["models"])
app.include_router(embeddings.router, prefix="/v1", tags=["embeddings"])

# Metrics endpoint
if settings.enable_metrics:
    app.get("/metrics", tags=["monitoring"])(get_metrics)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI UA",
        "version": "1.0.0",
        "description": "Local Gemini-compatible API with Ukrainian MamayLM model",
        "model": settings.model_name,
        "status": "ready" if inference_engine.is_loaded() else "loading",
        "endpoints": {
            "health": "/v1/health",
            "models": "/v1/models",
            "generate": "/v1/models/{model}/generateContent",
            "stream": "/v1/models/{model}/generateContentStream",
            "embed": "/v1/models/{model}/embedContent",
            "metrics": "/metrics",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
    )
