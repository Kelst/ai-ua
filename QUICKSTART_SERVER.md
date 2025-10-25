# Швидкий старт на Ubuntu Server

## Вимоги
- Ubuntu 22.04 LTS
- 20GB+ вільного місця (для моделі і Docker образів)
- 16GB+ RAM (рекомендовано 64GB+)
- Інтернет з'єднання для завантаження моделі

## Встановлення однією командою

```bash
# 1. Клонуйте репозиторій
git clone <your-repo-url> ai_ua
cd ai_ua

# 2. Запустіть автоматичне встановлення
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматично:
- Встановить Docker і Docker Compose (якщо потрібно)
- Встановить Python3 і необхідні залежності
- Завантажить модель MamayLM (8.23GB)
- Створить .env файл з оптимальними налаштуваннями
- Зібере Docker образи
- Запустить сервіси
- Перевірить, що все працює

**Очікуваний час**: 20-40 хвилин (залежить від швидкості інтернету)

## Налаштування для вашого сервера

Після встановлення відредагуйте `.env` для оптимізації під ваше залізо:

```bash
nano .env
```

Рекомендовані налаштування для HP ProLiant DL360 Gen9 (2x Xeon E5-2697A v4):

```bash
# Використовуйте 75% від доступних потоків
MODEL_THREADS=48

# Максимальний контекст моделі
MODEL_CONTEXT_SIZE=128000

# Для кращої швидкості
MODEL_BATCH_SIZE=512

# Одночасні запити
MAX_CONCURRENT_REQUESTS=4
```

Перезапустіть після змін:
```bash
docker compose restart
```

## Перевірка роботи

```bash
# Перевірити статус
docker compose ps

# Перевірити здоров'я API
curl http://localhost:8000/v1/health | python3 -m json.tool

# Тест генерації
curl -X POST http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Привіт! Хто ти?"}], "role": "user"}],
    "generationConfig": {"maxOutputTokens": 50}
  }' | python3 -m json.tool

# Повний тест всіх endpoint'ів
./scripts/test_api.sh
```

## Корисні команди

```bash
# Переглянути логи
docker compose logs -f

# Тільки API логи
docker compose logs -f api

# Зупинити
docker compose down

# Перезапустити
docker compose restart

# Оновити після змін коду
git pull
docker compose build
docker compose up -d
```

## Очікувана продуктивність

На вашому сервері (64 ядра, 125GB RAM):
- **Швидкість генерації**: ~1-2 сек/токен
- **Відповідь (200 токенів)**: ~3-6 хвилин
- **Одночасні користувачі**: 4-8
- **Контекст**: до 128K токенів

## Моніторинг (опціонально)

Запустити Prometheus для метрик:

```bash
docker compose --profile monitoring up -d
```

Метрики доступні на http://localhost:9090

## Troubleshooting

**Проблема**: "Out of memory" під час запуску
```bash
# Зменшіть потоки в .env
MODEL_THREADS=32
docker compose restart
```

**Проблема**: Повільна генерація
```bash
# Збільшіть потоки (якщо є ресурси)
MODEL_THREADS=64
docker compose restart
```

**Проблема**: Модель не завантажилась
```bash
# Перевірити наявність файлу
ls -lh backend/models/

# Завантажити знову
python3 scripts/download_with_python.py
```

**Проблема**: Docker permission denied
```bash
# Додати користувача до групи docker
sudo usermod -aG docker $USER
# Вийти і увійти знову
```

## Наступні кроки

1. **Інтеграція в ваш проект**: Див. `examples/migration_guide.md`
2. **Production налаштування**: Див. `DEPLOYMENT.md` (Nginx, SSL, systemd)
3. **Client SDK**: Див. `client-sdk/README.md`

## Підтримка

- Документація: `README.md`
- API docs: http://localhost:8000/docs
- Issues: GitHub Issues
