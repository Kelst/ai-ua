/**
 * Type definitions for AI UA client (Gemini-compatible).
 */

export interface TextPart {
  text: string;
}

export interface Content {
  role: 'user' | 'model';
  parts: TextPart[];
}

export interface GenerationConfig {
  temperature?: number;
  maxOutputTokens?: number;
  topK?: number;
  topP?: number;
  stopSequences?: string[];
}

export interface GenerateContentRequest {
  contents: Content[];
  generationConfig?: GenerationConfig;
}

export interface UsageMetadata {
  promptTokenCount: number;
  candidatesTokenCount: number;
  totalTokenCount: number;
  thoughtsTokenCount?: number;
  cachedContentTokenCount?: number;
}

export interface Candidate {
  content: Content;
  finishReason: string;
  index: number;
}

export interface GenerateContentResponse {
  candidates: Candidate[];
  usageMetadata?: UsageMetadata;
}

export interface ContentEmbedding {
  values: number[];
}

export interface EmbedContentResponse {
  embedding: ContentEmbedding;
}

export interface ModelParams {
  model: string;
}

export interface ClientConfig {
  apiUrl: string;
  timeout?: number;
}

/**
 * Helper class to access response text (Gemini compatibility).
 */
export class EnhancedGenerateContentResponse implements GenerateContentResponse {
  candidates: Candidate[];
  usageMetadata?: UsageMetadata;

  constructor(data: GenerateContentResponse) {
    this.candidates = data.candidates;
    this.usageMetadata = data.usageMetadata;
  }

  /**
   * Get text from first candidate.
   */
  text(): string {
    if (this.candidates && this.candidates[0]?.content?.parts?.[0]) {
      return this.candidates[0].content.parts[0].text;
    }
    return '';
  }
}

/**
 * Streaming chunk structure.
 */
export interface StreamChunk {
  candidates?: Candidate[];
  error?: string;
}
