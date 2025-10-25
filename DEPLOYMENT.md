# Deployment Guide - AI UA

Детальні інструкції по розгортанню AI UA на сервері.

## Системні вимоги

### Мінімальні
- CPU: 8 cores
- RAM: 16GB
- Disk: 20GB free space
- OS: Ubuntu 20.04+ / Debian 11+

### Рекомендовані (production)
- CPU: 16+ cores (ваш сервер: 64 threads)
- RAM: 32GB+ (ваш сервер: 125GB)
- Disk: 50GB+ SSD
- Network: 1Gbps+

## Підготовка сервера

### 1. Встановлення Docker

```bash
# Оновити систему
sudo apt update && sudo apt upgrade -y

# Встановити Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Додати користувача до групи docker
sudo usermod -aG docker $USER

# Перезавантажити сесію
newgrp docker

# Встановити Docker Compose
sudo apt install docker-compose-plugin
```

### 2. Підготовка директорій

```bash
# Створити робочу директорію
sudo mkdir -p /opt/ai_ua
sudo chown $USER:$USER /opt/ai_ua
cd /opt/ai_ua
```

## Локальна розробка

### 1. Клонування репозиторію

```bash
git clone <your-repo-url> .
```

### 2. Завантаження моделі

```bash
./scripts/download_model.sh
```

### 3. Налаштування конфігурації

```bash
cp .env.example .env

# Відредагувати .env
nano .env
```

Рекомендовані налаштування для вашого сервера (64 threads, 125GB RAM):

```bash
# Model Configuration
MODEL_THREADS=32           # Використовувати половину cores
MODEL_CONTEXT_SIZE=128000  # Повний контекст
MODEL_BATCH_SIZE=512

# Concurrency
MAX_CONCURRENT_REQUESTS=4  # Для 2-4 одночасних користувачів

# Logging
LOG_LEVEL=INFO
```

### 4. Запуск

```bash
# Перший запуск (збирає образи)
docker-compose up --build

# У фоновому режимі
docker-compose up -d --build

# Переглянути логи
docker-compose logs -f

# Тільки API логи
docker-compose logs -f api
```

### 5. Перевірка

```bash
# Health check
curl http://localhost:8000/v1/health

# Запустити тести
./scripts/test_api.sh
```

## Deployment на сервер

### Метод 1: Git Push

#### На локальній машині:

```bash
# Комміт змін
git add .
git commit -m "Initial AI UA setup"
git push origin main
```

#### На сервері:

```bash
# SSH на сервер
ssh vlad_b@ai

# Клонувати або pull
cd /opt/ai_ua
git clone <your-repo-url> .
# або
git pull origin main

# Завантажити модель
./scripts/download_model.sh

# Налаштувати .env
cp .env.example .env
nano .env

# Запустити
docker-compose up -d --build

# Перевірити статус
docker-compose ps
docker-compose logs -f
```

### Метод 2: SCP/rsync

```bash
# З локальної машини
rsync -avz --exclude 'backend/models/*.gguf' \
  --exclude 'node_modules' \
  --exclude '.git' \
  . vlad_b@ai:/opt/ai_ua/

# SSH на сервер і продовжити як у Методі 1
```

## Управління сервісами

### Основні команди

```bash
# Запуск
docker-compose up -d

# Зупинка
docker-compose down

# Рестарт
docker-compose restart

# Рестарт тільки API
docker-compose restart api

# Переглянути логи
docker-compose logs -f api

# Статус сервісів
docker-compose ps

# Використання ресурсів
docker stats
```

### Оновлення коду

```bash
# Pull нового коду
git pull origin main

# Перезбудувати та перезапустити
docker-compose down
docker-compose up -d --build

# Або без downtime (rolling update)
docker-compose up -d --build --no-deps api
```

### Оновлення моделі

```bash
# Зупинити API
docker-compose stop api

# Завантажити нову модель
./scripts/download_model.sh

# Запустити API
docker-compose start api
```

## Моніторинг

### Prometheus (опціонально)

```bash
# Запустити з моніторингом
docker-compose --profile monitoring up -d

# Доступ до Prometheus
http://<server-ip>:9090
```

### Метрики через API

```bash
# Подивитися метрики
curl http://localhost:8000/metrics

# Специфічні метрики
curl -s http://localhost:8000/metrics | grep inference_latency
curl -s http://localhost:8000/metrics | grep tokens_per_second
curl -s http://localhost:8000/metrics | grep active_requests
```

### Логування

```bash
# Всі логи
docker-compose logs -f

# Тільки помилки
docker-compose logs -f | grep ERROR

# Останні 100 рядків
docker-compose logs --tail=100 api

# З timestamp
docker-compose logs -f -t api
```

## Безпека

### 1. Firewall

```bash
# Дозволити тільки необхідні порти
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # API (або через Nginx)
sudo ufw enable
```

### 2. Nginx Reverse Proxy (рекомендовано)

```bash
# Встановити Nginx
sudo apt install nginx

# Створити конфігурацію
sudo nano /etc/nginx/sites-available/ai-ua
```

```nginx
server {
    listen 80;
    server_name ai.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # For streaming
        proxy_buffering off;
        proxy_cache off;
    }
}
```

```bash
# Активувати
sudo ln -s /etc/nginx/sites-available/ai-ua /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL (Let's Encrypt)

```bash
# Встановити certbot
sudo apt install certbot python3-certbot-nginx

# Отримати сертифікат
sudo certbot --nginx -d ai.yourdomain.com
```

## Troubleshooting

### API не стартує

```bash
# Перевірити логи
docker-compose logs api

# Перевірити модель
ls -lh backend/models/

# Перевірити конфігурацію
docker-compose config
```

### Out of Memory

```bash
# Перевірити використання пам'яті
free -h
docker stats

# Зменшити в .env:
MODEL_CONTEXT_SIZE=65536  # замість 128000
MAX_CONCURRENT_REQUESTS=2 # замість 4

# Рестарт
docker-compose restart api
```

### Повільна генерація

```bash
# Збільшити threads в .env
MODEL_THREADS=48  # більше cores

# Або використати меншу квантизацію
# Завантажити Q4_K_M замість Q5_K_M
```

### Embeddings service не працює

```bash
# Перевірити статус
docker-compose ps embeddings-service

# Перевірити логи
docker-compose logs embeddings-service

# Рестарт
docker-compose restart embeddings-service

# Якщо не допомагає, перезбудувати
docker-compose up -d --build embeddings-service
```

## Backup

### Конфігурація

```bash
# Backup .env
cp .env .env.backup

# Backup всієї конфігурації
tar -czf ai-ua-config-$(date +%Y%m%d).tar.gz \
  .env docker-compose.yml prometheus.yml
```

### Модель (якщо є custom fine-tune)

```bash
# Backup моделі
tar -czf model-backup-$(date +%Y%m%d).tar.gz backend/models/
```

## Автоматичний запуск

### Systemd service

```bash
# Створити service file
sudo nano /etc/systemd/system/ai-ua.service
```

```ini
[Unit]
Description=AI UA Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ai_ua
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Активувати
sudo systemctl enable ai-ua.service
sudo systemctl start ai-ua.service

# Перевірити статус
sudo systemctl status ai-ua.service
```

## Продуктивність

### Бенчмаркінг

```bash
# Простий тест
time curl -X POST http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"role":"user","parts":[{"text":"Hi"}]}]}'

# Load test (потрібен apache-bench)
sudo apt install apache2-utils
ab -n 100 -c 4 -p test.json -T application/json \
  http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent
```

### Очікувана продуктивність на вашому сервері

- **Latency**: ~100-200ms first token
- **Throughput**: ~30-50 tokens/s per request
- **Concurrent users**: 2-4 без черги
- **RAM usage**: ~12-15GB

## Контакти

Для питань створюйте issue у репозиторії.
