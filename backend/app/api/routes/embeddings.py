"""Embeddings endpoint - Gemini-compatible API."""
import logging
import httpx
from fastapi import APIRouter, HTTPException

from app.models.schemas import EmbedContentRequest, EmbedContentResponse, ContentEmbedding
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models/{model_name}/embedContent", response_model=EmbedContentResponse)
async def embed_content(model_name: str, request: EmbedContentRequest):
    """Generate embeddings for text (Gemini-compatible endpoint).

    Args:
        model_name: Model identifier (e.g., 'text-embedding-multilingual')
        request: Embed request with content

    Returns:
        EmbedContentResponse with embedding vector (768 dimensions)
    """
    try:
        # Call embeddings service
        embeddings_url = f"http://{settings.embeddings_host}:{settings.embeddings_port}/embed"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                embeddings_url,
                json={"text": request.content},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Embeddings service error: {response.text}",
                )

            data = response.json()
            embedding_values = data["embedding"]

            logger.info(f"Generated embedding with {len(embedding_values)} dimensions")

            return EmbedContentResponse(
                embedding=ContentEmbedding(values=embedding_values)
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to embeddings service: {e}")
        raise HTTPException(
            status_code=503,
            detail="Embeddings service unavailable",
        )
    except Exception as e:
        logger.error(f"Embedding error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
