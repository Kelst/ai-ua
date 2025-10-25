# Інструкції для деплою на сервер

## Перед деплоєм

1. **Закомітьте код на Mac:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI UA with MamayLM"
   ```

2. **Створіть репозиторій** (GitHub/GitLab/Gitea):
   - Або використайте приватний репозиторій
   - Або скопіюйте через scp/rsync

## Деплой на сервер Ubuntu

### Варіант 1: Через Git (рекомендовано)

```bash
# На сервері
git clone <your-repo-url> ai_ua
cd ai_ua
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматично:
- Встановить Docker (якщо потрібно)
- Завантажить модель (8.23GB)
- Створить .env
- Зібере образи
- Запустить сервіси
- Перевірить здоров'я

**Час деплою:** 20-40 хвилин

### Варіант 2: Через rsync (якщо модель вже завантажена)

На Mac:
```bash
# Скопіювати все на сервер
rsync -avz --exclude 'backend/models/*.gguf' \
  --exclude 'node_modules' \
  --exclude '.git' \
  ./ user@server:/path/to/ai_ua/

# Якщо модель вже завантажена на Mac, скопіювати її окремо
rsync -avz --progress \
  backend/models/mamay-gemma-3-12b-q5_k_s.gguf \
  user@server:/path/to/ai_ua/backend/models/
```

На сервері:
```bash
cd /path/to/ai_ua
chmod +x deploy.sh
./deploy.sh
```

## Після деплою

### 1. Перевірка статусу

```bash
# Статус контейнерів
docker compose ps

# Логи
docker compose logs -f

# Тільки API
docker compose logs -f api
```

### 2. Тест API

```bash
# Health check
curl http://localhost:8000/v1/health | python3 -m json.tool

# Тест генерації
curl -X POST http://localhost:8000/v1/models/mamay-gemma-3-12b/generateContent \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Привіт"}],"role":"user"}],"generationConfig":{"maxOutputTokens":20}}' \
  | python3 -m json.tool

# Повний тест
./scripts/test_api.sh
```

### 3. Оптимізація для вашого сервера

Відредагуйте `.env`:
```bash
nano .env
```

Рекомендовані налаштування:
```bash
MODEL_THREADS=48          # 75% від 64 потоків
MODEL_CONTEXT_SIZE=128000 # Максимальний контекст
MAX_CONCURRENT_REQUESTS=4 # Для 2+ користувачів
```

Перезапустіть:
```bash
docker compose restart
```

### 4. Автозапуск при перезавантаженні

Перевірте, що в `docker-compose.yml` стоїть `restart: unless-stopped` (вже налаштовано).

Або створіть systemd service:
```bash
sudo nano /etc/systemd/system/ai-ua.service
```

```ini
[Unit]
Description=AI UA Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/ai_ua
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=your-user

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ai-ua
sudo systemctl start ai-ua
```

## Troubleshooting

### Модель не завантажується
```bash
# Завантажити вручну
python3 scripts/download_with_python.py

# Перевірити
ls -lh backend/models/
```

### Out of memory
```bash
# Зменшити потоки
nano .env
# MODEL_THREADS=32
docker compose restart
```

### Повільна генерація
```bash
# Збільшити потоки
nano .env
# MODEL_THREADS=64
docker compose restart
```

### Docker permission denied
```bash
sudo usermod -aG docker $USER
# Вийти і увійти знову
```

## Моніторинг

### Базовий
```bash
# CPU/RAM
docker stats

# Логи в реальному часі
docker compose logs -f api
```

### Prometheus (опціонально)
```bash
docker compose --profile monitoring up -d
# Метрики: http://server-ip:9090
```

## Доступ ззовні

### Через Nginx (рекомендовано)

1. Встановити Nginx:
```bash
sudo apt install nginx
```

2. Налаштувати:
```bash
sudo nano /etc/nginx/sites-available/ai-ua
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 600s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-ua /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

3. SSL (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Через firewall
```bash
# Відкрити порт 8000
sudo ufw allow 8000/tcp
```

## Оновлення

```bash
# Зупинити
docker compose down

# Оновити код
git pull

# Перебудувати
docker compose build

# Запустити
docker compose up -d
```

## Резервне копіювання

### Що копіювати:
- `.env` - налаштування
- `backend/models/` - модель (якщо завантажена)
- `docker-compose.yml` - конфігурація

```bash
# Приклад backup
tar -czf ai-ua-backup-$(date +%Y%m%d).tar.gz \
  .env docker-compose.yml backend/models/
```

## Корисні команди

```bash
# Зупинити все
docker compose down

# Зупинити і видалити volumes
docker compose down -v

# Перезапустити API
docker compose restart api

# Переглянути використання ресурсів
docker stats

# Очистити Docker
docker system prune -a
```

## Підтримка

- Документація: `README.md`
- API docs: http://localhost:8000/docs
- Швидкий старт: `QUICKSTART_SERVER.md`
- Production: `DEPLOYMENT.md`
