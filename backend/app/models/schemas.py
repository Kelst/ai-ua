"""Pydantic models for Gemini-compatible API."""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ==================== Request Models ====================

class TextPart(BaseModel):
    """Text part of a message."""
    text: str


class Content(BaseModel):
    """Message content with role and parts."""
    role: Literal["user", "model"] = "user"
    parts: List[TextPart]


class GenerationConfig(BaseModel):
    """Generation configuration parameters."""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    maxOutputTokens: Optional[int] = Field(None, alias="max_output_tokens", ge=1)
    topK: Optional[int] = Field(None, alias="top_k", ge=1)
    topP: Optional[float] = Field(None, alias="top_p", ge=0.0, le=1.0)
    stopSequences: Optional[List[str]] = Field(None, alias="stop_sequences")

    class Config:
        populate_by_name = True


class GenerateContentRequest(BaseModel):
    """Request for generateContent endpoint."""
    contents: List[Content]
    generationConfig: Optional[GenerationConfig] = Field(None, alias="generation_config")

    class Config:
        populate_by_name = True


class EmbedContentRequest(BaseModel):
    """Request for embedContent endpoint."""
    content: str
    model: Optional[str] = None
    taskType: Optional[str] = Field(None, alias="task_type")
    title: Optional[str] = None

    class Config:
        populate_by_name = True


# ==================== Response Models ====================

class UsageMetadata(BaseModel):
    """Token usage metadata."""
    promptTokenCount: int = Field(..., alias="prompt_token_count")
    candidatesTokenCount: int = Field(..., alias="candidates_token_count")
    totalTokenCount: int = Field(..., alias="total_token_count")
    thoughtsTokenCount: int = Field(0, alias="thoughts_token_count")  # для сумісності
    cachedContentTokenCount: int = Field(0, alias="cached_content_token_count")  # для сумісності

    class Config:
        populate_by_name = True


class Candidate(BaseModel):
    """Response candidate."""
    content: Content
    finishReason: Optional[str] = Field("STOP", alias="finish_reason")
    index: int = 0

    class Config:
        populate_by_name = True


class GenerateContentResponse(BaseModel):
    """Response for generateContent endpoint."""
    candidates: List[Candidate]
    usageMetadata: Optional[UsageMetadata] = Field(None, alias="usage_metadata")

    @property
    def text(self) -> str:
        """Get text from first candidate (Gemini compatibility)."""
        if self.candidates and self.candidates[0].content.parts:
            return self.candidates[0].content.parts[0].text
        return ""

    class Config:
        populate_by_name = True


class ContentEmbedding(BaseModel):
    """Embedding vector."""
    values: List[float]


class EmbedContentResponse(BaseModel):
    """Response for embedContent endpoint."""
    embedding: ContentEmbedding


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    version: str
    displayName: str = Field(..., alias="display_name")
    description: str
    inputTokenLimit: int = Field(..., alias="input_token_limit")
    outputTokenLimit: int = Field(..., alias="output_token_limit")
    supportedGenerationMethods: List[str] = Field(..., alias="supported_generation_methods")

    class Config:
        populate_by_name = True


class ListModelsResponse(BaseModel):
    """Response for list models endpoint."""
    models: List[ModelInfo]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    gpu: bool
    version: str = "1.0.0"


# ==================== Internal Models ====================

class InferenceRequest(BaseModel):
    """Internal inference request."""
    prompt: str
    temperature: float = 0.3
    max_tokens: int = 8192
    top_k: int = 40
    top_p: float = 0.95
    stop: Optional[List[str]] = None
    stream: bool = False
