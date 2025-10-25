# AI UA - Локальна AI система на базі MamayLM-Gemma-3-12B

Це production-ready локальна AI система як заміна Google Gemini API з повною підтримкою української мови.

## Особливості

- 🇺🇦 **Українська модель**: MamayLM-Gemma-3-12B-IT (Q5_K_M квантизація)
- 🚀 **Швидка робота**: Оптимізовано для CPU inference на багатоядерних процесорах
- 🔄 **Concurrent processing**: Підтримка 2+ одночасних користувачів
- 📝 **Великий контекст**: До 128K токенів
- 🔌 **Gemini-compatible API**: Мінімальні зміни в існуючому коді
- 📊 **Моніторинг**: Prometheus метрики для production
- 🐳 **Docker**: Повністю контейнеризоване рішення

## Архітектура

```
┌─────────────────┐
│  Your App       │
│  (Node.js/TS)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────┐
│  AI API Service (FastAPI)       │
│  - /generateContent              │
│  - /generateContentStream        │
│  - /embedContent                 │
│  - /metrics                      │
└─────────┬───────────────────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐  ┌──────────────┐
│LlamaCPP│  │ Embeddings   │
│(GGUF)  │  │ Service      │
└────────┘  └──────────────┘
```

## Швидкий старт

### 1. Клонування репозиторію

```bash
git clone <your-repo-url> ai_ua
cd ai_ua
```

### 2. Завантаження моделі

```bash
# Завантаження GGUF моделі (Q5_K_M, ~8.23GB)
./scripts/download_model.sh
```

### 3. Налаштування конфігурації

```bash
cp .env.example .env
# Відредагуйте .env за потреби
```

### 4. Запуск через Docker Compose

```bash
docker-compose up --build
```

API буде доступне на `http://localhost:8000`

## Використання

### Приклад з Node.js Client SDK

```typescript
import { LocalGenerativeAI } from '@ai-ua/client';

// Ініціалізація (замість GoogleGenerativeAI)
const genAI = new LocalGenerativeAI({
  apiUrl: 'http://localhost:8000'
});

const model = genAI.getGenerativeModel({
  model: 'mamay-gemma-3-12b'
});

// Синхронна генерація
const result = await model.generateContent({
  contents: [{
    role: 'user',
    parts: [{ text: 'Привіт! Як справи?' }]
  }],
  generationConfig: {
    temperature: 0.3,
    maxOutputTokens: 8192
  }
});

console.log(result.response.text());

// Streaming
const streamResult = await model.generateContentStream({
  contents: [{ role: 'user', parts: [{ text: 'Розкажи про Київ' }] }]
});

for await (const chunk of streamResult.stream) {
  process.stdout.write(chunk.text());
}

// Embeddings
const embeddingModel = genAI.getGenerativeModel({
  model: 'text-embedding-multilingual'
});

const embedding = await embeddingModel.embedContent('Український текст');
console.log(embedding.embedding.values); // number[] (768 dimensions)
```

### Прямі HTTP запити

```bash
# Синхронна генерація
curl -X POST http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Привіт!"}]
    }],
    "generationConfig": {
      "temperature": 0.3,
      "maxOutputTokens": 1024
    }
  }'

# Embeddings
curl -X POST http://localhost:8000/v1/models/text-embedding-multilingual/embedContent \
  -H "Content-Type: application/json" \
  -d '{"content": "Український текст для векторизації"}'
```

## Deployment на сервер

### 1. На локальній машині

```bash
# Тестуємо локально
docker-compose up --build

# Коммітимо зміни
git add .
git commit -m "Initial AI UA setup"
git push origin main
```

### 2. На сервері (Ubuntu 22.04)

```bash
# SSH на сервер
ssh vlad_b@ai

# Клонуємо репо
cd /opt  # або інша директорія
git clone <your-repo-url> ai_ua
cd ai_ua

# Завантажуємо модель
./scripts/download_model.sh

# Налаштовуємо .env
cp .env.example .env
nano .env  # відредагувати за потреби

# Запускаємо
docker-compose up -d --build

# Перевіряємо логи
docker-compose logs -f

# Перевіряємо статус
curl http://localhost:8000/health
```

## Моніторинг

### Prometheus метрики

Доступні на `http://localhost:8000/metrics`:

- `inference_latency_seconds` - час генерації
- `tokens_per_second` - швидкість генерації
- `active_requests` - активні запити
- `queue_size` - розмір черги
- `model_memory_bytes` - використання пам'яті

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "model_loaded": true, "gpu": false}
```

## Системні вимоги

### Мінімальні
- CPU: 8 ядер
- RAM: 16GB
- Диск: 20GB вільного місця

### Рекомендовані (для production)
- CPU: 16+ ядер (наш сервер: 2x Xeon E5-2697A v4, 64 threads)
- RAM: 32GB+ (наш сервер: 125GB)
- Диск: 50GB+ SSD
- Мережа: 1Gbps+

## Продуктивність

На сервері HP ProLiant DL360 Gen9 (2x Xeon E5-2697A v4):

- **First token latency**: ~100-200ms
- **Throughput**: ~30-50 tokens/s (на запит)
- **Concurrent users**: 2-4 без черги, більше з чергою
- **RAM usage**: ~12-15GB (модель + контекст)
- **CPU usage**: ~30-50% при активній генерації

## Структура проекту

```
ai_ua/
├── backend/              # FastAPI сервіс
├── embeddings-service/   # Окремий сервіс для векторизації
├── client-sdk/           # Node.js/TypeScript SDK
├── scripts/              # Утилітні скрипти
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Модель не завантажується

```bash
# Перевірте наявність файлу
ls -lh backend/models/

# Перезавантажте контейнер
docker-compose restart api
```

### Повільна генерація

1. Збільште `MODEL_THREADS` в .env (до кількості CPU cores)
2. Зменште `MODEL_CONTEXT_SIZE` якщо не потрібен великий контекст
3. Використайте Q4_K_M квантизацію замість Q5_K_M

### Out of Memory

1. Зменште `MAX_CONCURRENT_REQUESTS`
2. Використайте меншу квантизацію (Q4 замість Q5)
3. Зменште `MODEL_CONTEXT_SIZE`

## Ліцензія

Це проект підпадає під Gemma Terms of Use від Google.

## Підтримка

Для питань та issues створюйте issue в цьому репозиторії.
