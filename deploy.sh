#!/bin/bash
# AI UA - Automated Deployment Script for Ubuntu Server
# This script sets up and deploys the AI UA system in one command

set -e  # Exit on any error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AI UA - Automated Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}➜${NC} $1"
}

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    print_error "This script is designed for Ubuntu/Debian systems"
    exit 1
fi

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_info "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose plugin not found"
    exit 1
else
    print_success "Docker Compose available"
fi

# Check if Python3 and pip are installed
if ! command -v python3 &> /dev/null; then
    print_info "Installing Python3..."
    sudo apt-get install -y python3 python3-pip
    print_success "Python3 installed"
else
    print_success "Python3 already installed"
fi

# Step 2: Install huggingface_hub for model download
print_info "Installing huggingface_hub..."
pip3 install -q huggingface_hub
print_success "huggingface_hub installed"

# Step 3: Create .env file
if [ ! -f .env ]; then
    print_info "Creating .env file from .env.example..."
    cp .env.example .env
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Step 4: Download model
print_info "Checking model file..."
if [ ! -f "backend/models/mamay-gemma-3-12b-q5_k_s.gguf" ]; then
    print_info "Downloading MamayLM model (8.23GB)..."
    print_info "This may take 10-30 minutes depending on your connection"
    python3 scripts/download_with_python.py
    print_success "Model downloaded"
else
    print_success "Model already downloaded"
fi

# Step 5: Build Docker images
print_info "Building Docker images..."
print_info "This may take 10-15 minutes on first run..."
docker compose build
print_success "Docker images built"

# Step 6: Start services
print_info "Starting services..."
docker compose up -d
print_success "Services started"

# Step 7: Wait for services to be healthy
print_info "Waiting for services to be ready..."
print_info "Embeddings service is starting (60-90 seconds)..."
sleep 60

print_info "API service is loading model (90-120 seconds)..."
MAX_WAIT=180
COUNTER=0
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8000/v1/health | grep -q "healthy"; then
        print_success "API service is ready!"
        break
    fi
    sleep 5
    COUNTER=$((COUNTER + 5))
    echo -n "."
done
echo ""

if [ $COUNTER -ge $MAX_WAIT ]; then
    print_error "Service did not become healthy in time"
    print_info "Check logs with: docker compose logs"
    exit 1
fi

# Step 8: Run health check
print_info "Running health check..."
HEALTH=$(curl -s http://localhost:8000/v1/health)
echo "$HEALTH" | python3 -m json.tool
print_success "Health check passed!"

# Step 9: Display summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Services running:"
echo "  - API: http://localhost:8000"
echo "  - Embeddings: http://localhost:8001"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart services: docker compose restart"
echo "  - Test API: ./scripts/test_api.sh"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
