.PHONY: help install build up down restart logs test clean download-model client-build

# Default target
help:
	@echo "AI UA - Make Commands"
	@echo "===================="
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies"
	@echo "  make download-model   - Download GGUF model from HuggingFace"
	@echo ""
	@echo "Docker:"
	@echo "  make build           - Build Docker images"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs (all services)"
	@echo "  make logs-api        - View API logs only"
	@echo "  make logs-embeddings - View embeddings service logs"
	@echo ""
	@echo "Development:"
	@echo "  make test            - Test API endpoints"
	@echo "  make client-build    - Build TypeScript client SDK"
	@echo "  make clean           - Clean up containers and volumes"
	@echo ""
	@echo "Monitoring:"
	@echo "  make up-monitoring   - Start with Prometheus monitoring"
	@echo "  make metrics         - View current metrics"
	@echo ""

# Installation
install:
	@echo "Checking prerequisites..."
	@which docker >/dev/null || (echo "Docker not found! Install from https://docs.docker.com/get-docker/" && exit 1)
	@which docker-compose >/dev/null || (echo "Docker Compose not found!" && exit 1)
	@echo "Prerequisites OK"
	@echo ""
	@echo "Creating .env from .env.example..."
	@test -f .env || cp .env.example .env
	@echo "Done! Edit .env if needed."

# Download model
download-model:
	@echo "Downloading MamayLM-Gemma-3-12B model..."
	@chmod +x scripts/download_model.sh
	@./scripts/download_model.sh

# Docker operations
build:
	docker compose build

up:
	docker compose up -d
	@echo ""
	@echo "Services starting..."
	@echo "API will be available at: http://localhost:8000"
	@echo "Check logs: make logs"
	@echo "Check health: curl http://localhost:8000/v1/health"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-embeddings:
	docker compose logs -f embeddings-service

# Monitoring
up-monitoring:
	docker compose --profile monitoring up -d
	@echo ""
	@echo "Services with monitoring starting..."
	@echo "API: http://localhost:8000"
	@echo "Prometheus: http://localhost:9090"

metrics:
	@curl -s http://localhost:8000/metrics | grep -E "^(api_requests_total|inference_latency_seconds|tokens_per_second|active_requests)" || echo "API not running or metrics not available"

# Testing
test:
	@echo "Testing API endpoints..."
	@chmod +x scripts/test_api.sh
	@./scripts/test_api.sh

# Client SDK
client-build:
	@echo "Building TypeScript client SDK..."
	cd client-sdk && npm install && npm run build
	@echo "Client SDK built successfully!"
	@echo "To use locally: cd client-sdk && npm link"

# Cleanup
clean:
	docker compose down -v
	@echo "Cleaned up containers and volumes"

# Quick start (for first time setup)
quickstart: install download-model build up
	@echo ""
	@echo "=========================================="
	@echo "AI UA is starting!"
	@echo "=========================================="
	@echo ""
	@echo "Wait ~2 minutes for services to initialize..."
	@echo "Then test with: make test"
	@echo ""
	@echo "API Endpoints:"
	@echo "  - Health: http://localhost:8000/v1/health"
	@echo "  - Models: http://localhost:8000/v1/models"
	@echo "  - Metrics: http://localhost:8000/metrics"
	@echo ""
	@echo "View logs: make logs"
	@echo ""
