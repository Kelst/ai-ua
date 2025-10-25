/**
 * LocalGenerativeAI client - Gemini-compatible interface.
 */
import { GenerativeModel } from './model';
import { ClientConfig, ModelParams } from './types';

export class LocalGenerativeAI {
  private apiUrl: string;
  private timeout: number;

  constructor(config: ClientConfig) {
    this.apiUrl = config.apiUrl;
    this.timeout = config.timeout || 300000;
  }

  /**
   * Get a generative model instance (Gemini-compatible).
   */
  getGenerativeModel(params: ModelParams): GenerativeModel {
    return new GenerativeModel({
      model: params.model,
      apiUrl: this.apiUrl,
      timeout: this.timeout,
    });
  }
}
