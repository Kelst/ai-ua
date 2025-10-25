#!/bin/bash
# Monitor model download progress

TOTAL_MB=8230

while true; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📥 Завантаження моделі MamayLM-Gemma-3-12B"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [ -d "backend/models" ]; then
    SIZE_MB=$(du -sm backend/models/ 2>/dev/null | cut -f1)
    SIZE_GB=$(echo "scale=2; $SIZE_MB / 1024" | bc)
    PERCENT=$(echo "scale=1; $SIZE_MB * 100 / $TOTAL_MB" | bc)

    echo "Завантажено: ${SIZE_GB}GB / 8.23GB (${PERCENT}%)"

    # Check if complete
    if [ "$SIZE_MB" -ge 8000 ]; then
      echo ""
      echo "✅ Завантаження завершено!"
      ls -lh backend/models/*.gguf
      exit 0
    fi
  fi

  echo ""
  echo "Наступне оновлення через 30 сек..."
  sleep 30
  clear
done
