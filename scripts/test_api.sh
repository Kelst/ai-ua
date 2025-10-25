#!/bin/bash
# Test AI UA API endpoints

API_URL="${1:-http://localhost:8000}"

echo "=========================================="
echo "AI UA API Testing"
echo "=========================================="
echo "API URL: $API_URL"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$API_URL/v1/health" | python3 -m json.tool
echo ""

# Test models list
echo "2. Testing models list..."
curl -s "$API_URL/v1/models" | python3 -m json.tool
echo ""

# Test generation
echo "3. Testing text generation..."
curl -s -X POST "$API_URL/v1/models/mamay-gemma-3-12b/generateContent" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Привіт! Як тебе звати?"}]
    }],
    "generationConfig": {
      "temperature": 0.3,
      "maxOutputTokens": 512
    }
  }' | python3 -m json.tool
echo ""

# Test embeddings
echo "4. Testing embeddings..."
curl -s -X POST "$API_URL/v1/models/text-embedding-multilingual/embedContent" \
  -H "Content-Type: application/json" \
  -d '{"content": "Тестовий текст для векторизації"}' \
  | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Dimensions: {len(data[\"embedding\"][\"values\"])}')"
echo ""

# Test metrics
echo "5. Testing metrics endpoint..."
curl -s "$API_URL/metrics" | grep -E "^(api_requests_total|inference_latency_seconds)" | head -5
echo ""

echo "=========================================="
echo "Testing complete!"
echo "=========================================="
