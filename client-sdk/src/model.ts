/**
 * GenerativeModel class - Gemini-compatible interface.
 */
import fetch from 'node-fetch';
import {
  Content,
  GenerationConfig,
  GenerateContentRequest,
  GenerateContentResponse,
  EnhancedGenerateContentResponse,
  EmbedContentResponse,
  StreamChunk,
} from './types';

export interface GenerativeModelParams {
  model: string;
  apiUrl: string;
  timeout?: number;
}

export class GenerativeModel {
  private model: string;
  private apiUrl: string;
  private timeout: number;

  constructor(params: GenerativeModelParams) {
    this.model = params.model;
    this.apiUrl = params.apiUrl;
    this.timeout = params.timeout || 300000; // 5 minutes default
  }

  /**
   * Generate content synchronously (Gemini-compatible).
   */
  async generateContent(request: GenerateContentRequest): Promise<{ response: EnhancedGenerateContentResponse }> {
    const url = `${this.apiUrl}/v1/models/${this.model}/generateContent`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.timeout),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API error (${response.status}): ${error}`);
      }

      const data = (await response.json()) as GenerateContentResponse;
      return {
        response: new EnhancedGenerateContentResponse(data),
      };
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to generate content: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Generate content with streaming (Gemini-compatible).
   */
  async generateContentStream(request: GenerateContentRequest): Promise<{
    stream: AsyncIterable<{ text: () => string }>;
  }> {
    const url = `${this.apiUrl}/v1/models/${this.model}/generateContentStream`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API error (${response.status}): ${error}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      // Create async iterable for streaming
      const asyncIterable = this.createAsyncIterable(response.body);

      return {
        stream: asyncIterable,
      };
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to stream content: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Create async iterable from SSE stream.
   */
  private async *createAsyncIterable(body: NodeJS.ReadableStream): AsyncIterable<{ text: () => string }> {
    const reader = body;
    let buffer = '';

    for await (const chunk of reader) {
      buffer += chunk.toString();

      // Process complete SSE messages
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6);
          try {
            const data = JSON.parse(jsonStr) as StreamChunk;

            if (data.error) {
              throw new Error(data.error);
            }

            if (data.candidates && data.candidates[0]?.content?.parts?.[0]) {
              const text = data.candidates[0].content.parts[0].text;
              yield {
                text: () => text,
              };
            }
          } catch (e) {
            // Skip invalid JSON
            console.warn('Failed to parse SSE chunk:', e);
          }
        }
      }
    }
  }

  /**
   * Generate embeddings (Gemini-compatible).
   */
  async embedContent(text: string): Promise<EmbedContentResponse> {
    const url = `${this.apiUrl}/v1/models/${this.model}/embedContent`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: text }),
        signal: AbortSignal.timeout(this.timeout),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API error (${response.status}): ${error}`);
      }

      const data = (await response.json()) as EmbedContentResponse;
      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to generate embedding: ${error.message}`);
      }
      throw error;
    }
  }
}
