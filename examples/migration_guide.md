# Міграція з Google Gemini на AI UA

Цей гайд допоможе вам мігрувати існуючий код з Google Gemini API на локальну AI UA систему.

## Швидка міграція

### Крок 1: Встановлення клієнта

```bash
npm install @ai-ua/client
# або
cd client-sdk && npm install && npm run build && npm link
```

### Крок 2: Заміна ініціалізації

**До:**
```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
```

**Після:**
```typescript
import { LocalGenerativeAI } from '@ai-ua/client';

const genAI = new LocalGenerativeAI({ apiUrl: 'http://localhost:8000' });
const model = genAI.getGenerativeModel({ model: 'mamay-gemma-3-12b' });
```

### Крок 3: Решта коду залишається без змін

Всі методи (`generateContent`, `generateContentStream`, `embedContent`) працюють так само!

## Детальна міграція для RAG системи

### 1. Генерація тексту

**Gemini код (без змін):**
```typescript
const result = await model.generateContent({
  contents: [{
    role: 'user',
    parts: [{ text: prompt }]
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
```

Працює без змін з AI UA!

### 2. Streaming

**Gemini код (без змін):**
```typescript
const result = await model.generateContentStream({
  contents: [{ role: 'user', parts: [{ text: prompt }] }],
  generationConfig,
});

for await (const chunk of result.stream) {
  const chunkText = chunk.text();
  yield chunkText;
}
```

Працює без змін з AI UA!

### 3. Embeddings

**До (Gemini):**
```typescript
const model = genAI.getGenerativeModel({
  model: 'text-embedding-004'
});

const result = await model.embedContent(text);
const embedding = result.embedding.values; // 768 dimensions
```

**Після (AI UA):**
```typescript
const model = genAI.getGenerativeModel({
  model: 'text-embedding-multilingual'  // змінено назву моделі
});

const result = await model.embedContent(text);
const embedding = result.embedding.values; // 768 dimensions
```

Єдина зміна - назва моделі!

## Оновлення існуючого RAG проекту

### Варіант 1: Заміна через змінні середовища

Створіть wrapper файл `src/lib/ai-client.ts`:

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';
import { LocalGenerativeAI } from '@ai-ua/client';

const USE_LOCAL = process.env.USE_LOCAL_AI === 'true';

export function getAIClient() {
  if (USE_LOCAL) {
    return new LocalGenerativeAI({
      apiUrl: process.env.AI_UA_URL || 'http://localhost:8000'
    });
  } else {
    return new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  }
}

// Використання:
// const genAI = getAIClient();
```

### Варіант 2: Повна заміна

У вашому сервісі (наприклад, `gemini.service.ts`):

```typescript
// Було:
// import { GoogleGenerativeAI } from '@google/generative-ai';
// const genAI = new GoogleGenerativeAI(apiKey);

// Стало:
import { LocalGenerativeAI } from '@ai-ua/client';
const genAI = new LocalGenerativeAI({
  apiUrl: process.env.AI_UA_URL || 'http://localhost:8000'
});
```

Решта коду залишається без змін!

## Оновлення конфігурації

### Environment variables

Додайте до `.env`:

```bash
# AI Configuration
USE_LOCAL_AI=true
AI_UA_URL=http://localhost:8000

# Fallback to Gemini (optional)
GEMINI_API_KEY=your-key-here
```

### Model mappings

| Gemini Model | AI UA Model |
|-------------|------------|
| `gemini-2.5-flash` | `mamay-gemma-3-12b` |
| `text-embedding-004` | `text-embedding-multilingual` |

## Відмінності та обмеження

### Що працює однаково:
- ✅ `generateContent()` - синхронна генерація
- ✅ `generateContentStream()` - streaming
- ✅ `embedContent()` - векторизація
- ✅ `usageMetadata` - підрахунок токенів
- ✅ Формат запитів і відповідей

### Що відрізняється:
- ⚠️ Назви моделей (див. таблицю вище)
- ⚠️ `thoughtsTokenCount` завжди 0 (немає reasoning mode)
- ⚠️ `cachedContentTokenCount` завжди 0 (немає кешування)
- ⚠️ Швидкість залежить від вашого сервера

### Що не підтримується:
- ❌ Мультимодальність (зображення, відео)
- ❌ Функції та tool calling
- ❌ Safety settings
- ❌ Context caching

## Тестування після міграції

1. **Перевірте генерацію:**
```bash
npm test
# або
node examples/basic_usage.js
```

2. **Перевірте embeddings:**
```bash
# Розмірність має бути 768
curl -X POST http://localhost:8000/v1/models/text-embedding-multilingual/embedContent \
  -H "Content-Type: application/json" \
  -d '{"content": "test"}' | jq '.embedding.values | length'
```

3. **Перевірте streaming:**
```typescript
// Має виводити текст поступово
const result = await model.generateContentStream({...});
for await (const chunk of result.stream) {
  console.log(chunk.text());
}
```

## Troubleshooting

### API не відповідає
```bash
# Перевірте, чи працює сервер
curl http://localhost:8000/v1/health

# Перевірте логи
docker-compose logs -f api
```

### Помилка з embeddings
```bash
# Перевірте embeddings service
curl http://localhost:8001/health

# Рестарт контейнера
docker-compose restart embeddings-service
```

### Повільна генерація
```bash
# Збільште кількість threads в .env
MODEL_THREADS=32

# Або використайте меншу квантизацію
# Q4_K_M замість Q5_K_M
```

## Підтримка

Якщо виникли питання або проблеми, створіть issue у репозиторії проекту.
