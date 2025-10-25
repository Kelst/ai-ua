"""Generation endpoints - Gemini-compatible API."""
import logging
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from app.models.schemas import (
    GenerateContentRequest,
    GenerateContentResponse,
    Candidate,
    Content,
    TextPart,
    UsageMetadata,
)
from app.core.inference import inference_engine
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models/{model_name}/generateContent", response_model=GenerateContentResponse)
async def generate_content(model_name: str, request: GenerateContentRequest):
    """Generate content synchronously (Gemini-compatible endpoint).

    Args:
        model_name: Model identifier (e.g., 'mamay-gemma-3-12b')
        request: Generation request with contents and config

    Returns:
        GenerateContentResponse with generated text and usage metadata
    """
    if not inference_engine.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Format chat prompt
        contents_dict = [c.model_dump() for c in request.contents]
        prompt = inference_engine.format_chat_prompt(contents_dict)

        logger.info(f"Generate request for model: {model_name}")
        logger.debug(f"Prompt length: {len(prompt)} chars")

        # Get generation config or use defaults
        config = request.generationConfig or {}
        temperature = config.temperature if config.temperature is not None else settings.default_temperature
        max_tokens = config.maxOutputTokens if config.maxOutputTokens is not None else settings.default_max_tokens
        top_k = config.topK if config.topK is not None else settings.default_top_k
        top_p = config.topP if config.topP is not None else settings.default_top_p
        stop = config.stopSequences or ["<end_of_turn>"]

        # Generate
        start_time = time.time()
        result = await inference_engine.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_k=top_k,
            top_p=top_p,
            stop=stop,
        )
        elapsed = time.time() - start_time

        logger.info(
            f"Generated {result['completion_tokens']} tokens in {elapsed:.2f}s "
            f"({result['completion_tokens']/elapsed:.1f} tok/s)"
        )

        # Build response in Gemini format
        response = GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        role="model",
                        parts=[TextPart(text=result["text"])],
                    ),
                    finishReason="STOP",
                    index=0,
                )
            ],
            usageMetadata=UsageMetadata(
                promptTokenCount=result["prompt_tokens"],
                candidatesTokenCount=result["completion_tokens"],
                totalTokenCount=result["total_tokens"],
            ),
        )

        return response

    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/generateContentStream")
async def generate_content_stream(model_name: str, request: GenerateContentRequest):
    """Generate content with streaming (Gemini-compatible endpoint).

    Args:
        model_name: Model identifier
        request: Generation request

    Returns:
        Streaming response with SSE format
    """
    if not inference_engine.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Format chat prompt
        contents_dict = [c.model_dump() for c in request.contents]
        prompt = inference_engine.format_chat_prompt(contents_dict)

        logger.info(f"Stream request for model: {model_name}")

        # Get generation config or use defaults
        config = request.generationConfig or {}
        temperature = config.temperature if config.temperature is not None else settings.default_temperature
        max_tokens = config.maxOutputTokens if config.maxOutputTokens is not None else settings.default_max_tokens
        top_k = config.topK if config.topK is not None else settings.default_top_k
        top_p = config.topP if config.topP is not None else settings.default_top_p
        stop = config.stopSequences or ["<end_of_turn>"]

        async def stream_generator() -> AsyncGenerator[bytes, None]:
            """Generate SSE stream."""
            try:
                async for chunk_text in inference_engine.generate_stream(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_k=top_k,
                    top_p=top_p,
                    stop=stop,
                ):
                    # Format as Gemini-style JSON chunk
                    chunk_response = {
                        "candidates": [
                            {
                                "content": {
                                    "role": "model",
                                    "parts": [{"text": chunk_text}],
                                },
                                "finishReason": None,
                                "index": 0,
                            }
                        ],
                    }

                    # Send as JSON
                    import json
                    yield f"data: {json.dumps(chunk_response)}\n\n".encode("utf-8")

                # Send final chunk with finish reason
                final_chunk = {
                    "candidates": [
                        {
                            "content": {"role": "model", "parts": [{"text": ""}]},
                            "finishReason": "STOP",
                            "index": 0,
                        }
                    ],
                }
                import json
                yield f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8")

            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                error_chunk = {"error": str(e)}
                import json
                yield f"data: {json.dumps(error_chunk)}\n\n".encode("utf-8")

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        logger.error(f"Stream setup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
