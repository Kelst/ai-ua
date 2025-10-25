/**
 * AI UA Client SDK
 * Gemini-compatible API for local Ukrainian AI model.
 */

export { LocalGenerativeAI } from './client';
export { GenerativeModel } from './model';
export type {
  ClientConfig,
  ModelParams,
  Content,
  TextPart,
  GenerationConfig,
  GenerateContentRequest,
  GenerateContentResponse,
  UsageMetadata,
  Candidate,
  EmbedContentResponse,
  ContentEmbedding,
} from './types';
