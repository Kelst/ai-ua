# Швидкий старт - AI UA

Мінімальні кроки для запуску AI UA за 5 хвилин.

## 1. Передумови

Переконайтесь, що у вас встановлено:
- Docker (версія 20.10+)
- Docker Compose (версія 2.0+)
- Git
- 20GB+ вільного місця на диску

Перевірка:
```bash
docker --version
docker-compose --version
git --version
```

## 2. Клонування проекту

```bash
git clone <your-repo-url> ai_ua
cd ai_ua
```

## 3. Швидкий старт з Make

```bash
# Один крок - все автоматично
make quickstart
```

Це виконає:
1. Створить `.env` з `.env.example`
2. Завантажить модель (8.23GB, ~10-30 хв)
3. Збудує Docker образи
4. Запустить всі сервіси

## 4. Перевірка

Почекайте ~2 хвилини після `make quickstart`, потім:

```bash
# Перевірити здоров'я API
curl http://localhost:8000/v1/health

# Запустити тести
make test
```

Очікуваний результат:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu": false,
  "version": "1.0.0"
}
```

## 5. Перший запит

```bash
curl -X POST http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Привіт! Як справи?"}]
    }],
    "generationConfig": {
      "temperature": 0.3,
      "maxOutputTokens": 512
    }
  }'
```

## Альтернатива: Ручний запуск

Якщо `make` недоступний:

### Крок 1: Налаштування

```bash
cp .env.example .env
# Відредагувати .env за потреби (необов'язково для початку)
```

### Крок 2: Завантаження моделі

```bash
chmod +x scripts/download_model.sh
./scripts/download_model.sh
```

### Крок 3: Запуск

```bash
docker-compose up --build -d
```

### Крок 4: Перевірка

```bash
# Переглянути логи
docker-compose logs -f

# Перевірити здоров'я (в іншому терміналі)
curl http://localhost:8000/v1/health

# Тест
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

## Використання з Node.js

### 1. Збудувати клієнт

```bash
make client-build
cd client-sdk && npm link
```

### 2. У вашому проекті

```bash
npm link @ai-ua/client
```

### 3. Код

```typescript
import { LocalGenerativeAI } from '@ai-ua/client';

const genAI = new LocalGenerativeAI({
  apiUrl: 'http://localhost:8000'
});

const model = genAI.getGenerativeModel({
  model: 'mamay-gemma-3-12b'
});

const result = await model.generateContent({
  contents: [{
    role: 'user',
    parts: [{ text: 'Привіт!' }]
  }]
});

console.log(result.response.text());
```

## Корисні команди

```bash
# Переглянути логи
make logs

# Перезапустити
make restart

# Зупинити
make down

# Метрики
make metrics

# Очистити все
make clean
```

## Troubleshooting

### Модель не завантажується?

```bash
# Перевірити розмір файлу
ls -lh backend/models/mamay-gemma-3-12b-q5_k_m.gguf

# Має бути ~8.23GB. Якщо менше, завантажте знову:
rm backend/models/mamay-gemma-3-12b-q5_k_m.gguf
make download-model
```

### API не відповідає?

```bash
# Переглянути логи
docker-compose logs api

# Перевірити статус контейнерів
docker-compose ps

# Рестарт
make restart
```

### Out of Memory?

Зменшіть у `.env`:
```bash
MODEL_CONTEXT_SIZE=65536  # замість 128000
MAX_CONCURRENT_REQUESTS=2 # замість 4
```

Потім:
```bash
make restart
```

## Наступні кроки

1. **Інтеграція**: Див. `examples/migration_guide.md`
2. **Deployment**: Див. `DEPLOYMENT.md`
3. **API Docs**: Див. `README.md`

## Підтримка

Створіть issue у репозиторії для питань або проблем.
