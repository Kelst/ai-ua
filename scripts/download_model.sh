#!/bin/bash
# Download MamayLM-Gemma-3-12B GGUF model from HuggingFace

set -e

MODEL_DIR="backend/models"
MODEL_FILE="mamay-gemma-3-12b-q5_k_m.gguf"
# Use cdn endpoint for direct download
MODEL_URL="https://huggingface.co/INSAIT-Institute/MamayLM-Gemma-3-12B-IT-v1.0-GGUF/resolve/main/mamay-gemma-3-12b-it-v1.0-q5_k_m.gguf?download=true"

echo "=========================================="
echo "AI UA Model Downloader"
echo "=========================================="
echo ""
echo "Model: MamayLM-Gemma-3-12B-IT (Q5_K_M)"
echo "Size: ~8.23 GB"
echo "Target: $MODEL_DIR/$MODEL_FILE"
echo ""

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model already exists
if [ -f "$MODEL_DIR/$MODEL_FILE" ]; then
    echo "Model already exists at $MODEL_DIR/$MODEL_FILE"
    echo "Size: $(du -h "$MODEL_DIR/$MODEL_FILE" | cut -f1)"
    read -p "Re-download? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
    rm -f "$MODEL_DIR/$MODEL_FILE"
fi

# Check for wget or curl
if command -v wget &> /dev/null; then
    DOWNLOADER="wget"
    echo "Using wget for download..."
elif command -v curl &> /dev/null; then
    DOWNLOADER="curl"
    echo "Using curl for download..."
else
    echo "Error: Neither wget nor curl found. Please install one of them."
    exit 1
fi

# Download model
echo "Downloading model..."
echo "This may take a while (8.23 GB)..."
echo ""

if [ "$DOWNLOADER" = "wget" ]; then
    wget --progress=bar:force:noscroll \
         --continue \
         -O "$MODEL_DIR/$MODEL_FILE" \
         "$MODEL_URL"
else
    curl -L \
         --progress-bar \
         --continue-at - \
         -o "$MODEL_DIR/$MODEL_FILE" \
         "$MODEL_URL"
fi

# Verify download
if [ -f "$MODEL_DIR/$MODEL_FILE" ]; then
    echo ""
    echo "=========================================="
    echo "Download complete!"
    echo "=========================================="
    echo "Model: $MODEL_FILE"
    echo "Size: $(du -h "$MODEL_DIR/$MODEL_FILE" | cut -f1)"
    echo "Location: $MODEL_DIR/$MODEL_FILE"
    echo ""
    echo "You can now run: docker-compose up --build"
else
    echo ""
    echo "Error: Download failed. File not found."
    exit 1
fi
