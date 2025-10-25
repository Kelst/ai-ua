"""Inference engine using llama-cpp-python."""
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from llama_cpp import Llama
from app.core.config import settings

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Manages model loading and inference with llama-cpp-python."""

    def __init__(self):
        self.model: Optional[Llama] = None
        self.executor = ThreadPoolExecutor(max_workers=settings.max_concurrent_requests)
        self._lock = asyncio.Lock()

    def load_model(self):
        """Load GGUF model into memory."""
        logger.info(f"Loading model from {settings.model_path}")
        logger.info(f"Context size: {settings.model_context_size}, Threads: {settings.model_threads}")

        try:
            self.model = Llama(
                model_path=settings.model_path,
                n_ctx=settings.model_context_size,
                n_threads=settings.model_threads,
                n_batch=settings.model_batch_size,
                n_gpu_layers=settings.model_gpu_layers,
                verbose=False,
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
        top_k: int = 40,
        top_p: float = 0.95,
        stop: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Generate text synchronously.

        Returns:
            Dict with 'text', 'prompt_tokens', 'completion_tokens', 'total_tokens'
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")

        loop = asyncio.get_event_loop()

        # Run inference in thread pool
        def _generate():
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                stop=stop or [],
                echo=False,
            )
            return response

        response = await loop.run_in_executor(self.executor, _generate)

        # Extract results
        text = response["choices"][0]["text"]
        usage = response.get("usage", {})

        return {
            "text": text,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
        top_k: int = 40,
        top_p: float = 0.95,
        stop: Optional[list[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming.

        Yields:
            Text chunks as they are generated
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")

        # Create a queue for streaming
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def _generate_stream():
            """Run streaming in thread."""
            try:
                stream = self.model(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    stop=stop or [],
                    echo=False,
                    stream=True,
                )

                for chunk in stream:
                    text = chunk["choices"][0]["text"]
                    asyncio.run_coroutine_threadsafe(queue.put(text), loop)

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        # Start streaming in background
        loop.run_in_executor(self.executor, _generate_stream)

        # Yield chunks
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    def format_chat_prompt(self, contents: list[Dict[str, Any]]) -> str:
        """Format chat messages into a prompt for Gemma model.

        Gemma-3 uses a specific format:
        <start_of_turn>user
        message<end_of_turn>
        <start_of_turn>model
        response<end_of_turn>
        """
        prompt_parts = []

        for content in contents:
            role = content.get("role", "user")
            parts = content.get("parts", [])

            # Extract text from parts
            text = ""
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    text += part["text"]

            # Format according to Gemma template
            if role == "user":
                prompt_parts.append(f"<start_of_turn>user\n{text}<end_of_turn>")
            elif role == "model":
                prompt_parts.append(f"<start_of_turn>model\n{text}<end_of_turn>")

        # Add model turn start for generation
        prompt_parts.append("<start_of_turn>model\n")

        return "\n".join(prompt_parts)

    def shutdown(self):
        """Cleanup resources."""
        logger.info("Shutting down inference engine")
        self.executor.shutdown(wait=True)
        if self.model:
            del self.model
            self.model = None


# Global inference engine instance
inference_engine = InferenceEngine()
