"""Embeddings service using sentence-transformers."""
import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model: Optional[SentenceTransformer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    global model

    logger.info(f"Loading embeddings model: {MODEL_NAME}")
    try:
        model = SentenceTransformer(MODEL_NAME)
        logger.info(f"Model loaded successfully - dimensions: {model.get_sentence_embedding_dimension()}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

    yield

    logger.info("Shutting down embeddings service")


app = FastAPI(
    title="Embeddings Service",
    description="Text embeddings service with multilingual support",
    version="1.0.0",
    lifespan=lifespan,
)


class EmbedRequest(BaseModel):
    """Embedding request."""
    text: str


class EmbedResponse(BaseModel):
    """Embedding response."""
    embedding: list[float]
    dimensions: int


@app.post("/embed", response_model=EmbedResponse)
async def create_embedding(request: EmbedRequest):
    """Generate embedding for text.

    Args:
        request: Text to embed

    Returns:
        Embedding vector (768 dimensions)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Generate embedding
        embedding = model.encode(request.text, convert_to_numpy=True)
        embedding_list = embedding.tolist()

        logger.debug(f"Generated embedding for text of length {len(request.text)}")

        return EmbedResponse(
            embedding=embedding_list,
            dimensions=len(embedding_list),
        )

    except Exception as e:
        logger.error(f"Embedding error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if model is not None else "model_not_loaded",
        "model": MODEL_NAME,
        "dimensions": model.get_sentence_embedding_dimension() if model else None,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Embeddings Service",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "status": "ready" if model is not None else "loading",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
