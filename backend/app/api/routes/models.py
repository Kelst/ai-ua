"""Models endpoint - list available models."""
import logging
from fastapi import APIRouter
from app.models.schemas import ListModelsResponse, ModelInfo, HealthResponse
from app.core.inference import inference_engine
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models", response_model=ListModelsResponse)
async def list_models():
    """List available models (Gemini-compatible endpoint).

    Returns:
        List of available models
    """
    models = [
        ModelInfo(
            name=settings.model_name,
            version="1.0",
            displayName="MamayLM Gemma 3 12B IT",
            description="Ukrainian-optimized Gemma 3 12B Instruct model (Q5_K_M quantization)",
            inputTokenLimit=settings.model_context_size,
            outputTokenLimit=settings.default_max_tokens,
            supportedGenerationMethods=["generateContent", "generateContentStream"],
        ),
        ModelInfo(
            name="text-embedding-multilingual",
            version="1.0",
            displayName="Multilingual Embeddings",
            description="Multilingual text embeddings (768 dimensions)",
            inputTokenLimit=512,
            outputTokenLimit=0,
            supportedGenerationMethods=["embedContent"],
        ),
    ]

    return ListModelsResponse(models=models)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.

    Returns:
        Health status with model information
    """
    return HealthResponse(
        status="healthy" if inference_engine.is_loaded() else "model_not_loaded",
        model_loaded=inference_engine.is_loaded(),
        gpu=settings.model_gpu_layers > 0,
    )
