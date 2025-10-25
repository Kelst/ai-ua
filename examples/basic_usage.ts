/**
 * Basic usage example for AI UA Client SDK
 *
 * This example shows how to migrate from Google Gemini to AI UA
 */

import { LocalGenerativeAI } from '@ai-ua/client';

async function main() {
  // Initialize client (replaces GoogleGenerativeAI)
  const genAI = new LocalGenerativeAI({
    apiUrl: process.env.AI_UA_URL || 'http://localhost:8000',
  });

  // Get model instance
  const model = genAI.getGenerativeModel({
    model: 'mamay-gemma-3-12b',
  });

  console.log('='.repeat(50));
  console.log('AI UA Client SDK - Basic Usage Example');
  console.log('='.repeat(50));
  console.log();

  // Example 1: Simple text generation
  console.log('1. Simple text generation:');
  console.log('-'.repeat(50));

  const result = await model.generateContent({
    contents: [{
      role: 'user',
      parts: [{ text: 'Привіт! Розкажи про себе коротко.' }],
    }],
    generationConfig: {
      temperature: 0.3,
      maxOutputTokens: 512,
    },
  });

  console.log('Response:', result.response.text());
  console.log();
  console.log('Metadata:');
  console.log('  Prompt tokens:', result.response.usageMetadata?.promptTokenCount);
  console.log('  Completion tokens:', result.response.usageMetadata?.candidatesTokenCount);
  console.log('  Total tokens:', result.response.usageMetadata?.totalTokenCount);
  console.log();

  // Example 2: Streaming generation
  console.log('2. Streaming generation:');
  console.log('-'.repeat(50));

  const streamResult = await model.generateContentStream({
    contents: [{
      role: 'user',
      parts: [{ text: 'Напиши короткий вірш про Київ.' }],
    }],
  });

  process.stdout.write('Response: ');
  for await (const chunk of streamResult.stream) {
    process.stdout.write(chunk.text());
  }
  console.log('\n');

  // Example 3: Chat conversation
  console.log('3. Chat conversation:');
  console.log('-'.repeat(50));

  const chatResult = await model.generateContent({
    contents: [
      {
        role: 'user',
        parts: [{ text: 'Привіт! Як справи?' }],
      },
      {
        role: 'model',
        parts: [{ text: 'Привіт! У мене все добре, дякую! Як я можу тобі допомогти?' }],
      },
      {
        role: 'user',
        parts: [{ text: 'Розкажи про українську культуру.' }],
      },
    ],
    generationConfig: {
      temperature: 0.5,
      maxOutputTokens: 1024,
    },
  });

  console.log('Response:', chatResult.response.text());
  console.log();

  // Example 4: Embeddings
  console.log('4. Text embeddings:');
  console.log('-'.repeat(50));

  const embeddingModel = genAI.getGenerativeModel({
    model: 'text-embedding-multilingual',
  });

  const embedding = await embeddingModel.embedContent('Український текст для векторизації');

  console.log('Embedding dimensions:', embedding.embedding.values.length);
  console.log('First 5 values:', embedding.embedding.values.slice(0, 5));
  console.log();

  console.log('='.repeat(50));
  console.log('All examples completed successfully!');
  console.log('='.repeat(50));
}

// Run examples
main().catch(console.error);
