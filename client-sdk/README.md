# AI UA Client SDK

Node.js/TypeScript клієнт для AI UA з Gemini-сумісним API.

## Встановлення

```bash
npm install @ai-ua/client
```

Або локально:

```bash
cd client-sdk
npm install
npm run build
npm link
```

У вашому проекті:

```bash
npm link @ai-ua/client
```

## Використання

### Заміна Google Gemini API

**До (з Google Gemini):**

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
```

**Після (з AI UA):**

```typescript
import { LocalGenerativeAI } from '@ai-ua/client';

const genAI = new LocalGenerativeAI({ apiUrl: 'http://localhost:8000' });
const model = genAI.getGenerativeModel({ model: 'mamay-gemma-3-12b' });
```

### Синхронна генерація

```typescript
const result = await model.generateContent({
  contents: [{
    role: 'user',
    parts: [{ text: 'Привіт! Як справи?' }]
  }],
  generationConfig: {
    temperature: 0.3,
    maxOutputTokens: 8192,
    topK: 40,
    topP: 0.95,
  }
});

const text = result.response.text();
const metadata = result.response.usageMetadata;
console.log(text);
console.log(`Tokens: ${metadata.totalTokenCount}`);
```

### Streaming генерація

```typescript
const result = await model.generateContentStream({
  contents: [{ role: 'user', parts: [{ text: 'Розкажи про Київ' }] }]
});

for await (const chunk of result.stream) {
  process.stdout.write(chunk.text());
}
```

### Embeddings

```typescript
const embeddingModel = genAI.getGenerativeModel({
  model: 'text-embedding-multilingual'
});

const result = await embeddingModel.embedContent('Український текст');
console.log(result.embedding.values); // number[] (768 dimensions)
```

## Міграція з існуючого коду

Якщо у вас вже є код з `@google/generative-ai`, замініть тільки ініціалізацію:

```typescript
// Старий код
// import { GoogleGenerativeAI } from '@google/generative-ai';
// const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Новий код
import { LocalGenerativeAI } from '@ai-ua/client';
const genAI = new LocalGenerativeAI({
  apiUrl: process.env.AI_UA_URL || 'http://localhost:8000'
});

// Решта коду залишається без змін!
const model = genAI.getGenerativeModel({ model: 'mamay-gemma-3-12b' });
const result = await model.generateContent({ /* ... */ });
```

## API Reference

### `LocalGenerativeAI`

Головний клас для ініціалізації.

#### Constructor

```typescript
new LocalGenerativeAI(config: ClientConfig)
```

**config:**
- `apiUrl` (string): URL AI UA API (наприклад, `http://localhost:8000`)
- `timeout?` (number): Timeout для запитів у мс (за замовчуванням: 300000)

#### Methods

##### `getGenerativeModel(params: ModelParams): GenerativeModel`

Отримати екземпляр моделі.

**params:**
- `model` (string): Назва моделі
  - `'mamay-gemma-3-12b'` - генеративна модель
  - `'text-embedding-multilingual'` - embeddings модель

### `GenerativeModel`

Клас для роботи з моделлю.

#### Methods

##### `generateContent(request: GenerateContentRequest): Promise<{response: EnhancedGenerateContentResponse}>`

Синхронна генерація тексту.

##### `generateContentStream(request: GenerateContentRequest): Promise<{stream: AsyncIterable<{text: () => string}>}>`

Streaming генерація.

##### `embedContent(text: string): Promise<EmbedContentResponse>`

Генерація embeddings.

## TypeScript Support

Бібліотека повністю типізована і містить всі необхідні TypeScript definitions.

## Ліцензія

MIT
