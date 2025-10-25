#!/usr/bin/env python3
"""Download model using huggingface_hub."""
import os
from huggingface_hub import hf_hub_download

# Configuration
repo_id = "INSAIT-Institute/MamayLM-Gemma-3-12B-IT-v1.0-GGUF"
filename = "MamayLM-Gemma-3-12B-IT-v1.0.Q5_K_S.gguf"
local_dir = "backend/models"
local_filename = "mamay-gemma-3-12b-q5_k_s.gguf"

print("=" * 50)
print("Downloading MamayLM-Gemma-3-12B model...")
print("=" * 50)
print(f"Repository: {repo_id}")
print(f"File: {filename}")
print(f"Size: ~8.23 GB")
print()

# Create directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

try:
    # Download with progress
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )

    # Rename to simpler name
    target_path = os.path.join(local_dir, local_filename)
    if downloaded_path != target_path and os.path.exists(downloaded_path):
        os.rename(downloaded_path, target_path)
        final_path = target_path
    else:
        final_path = downloaded_path

    # Get file size
    size_bytes = os.path.getsize(final_path)
    size_gb = size_bytes / (1024**3)

    print()
    print("=" * 50)
    print("Download complete!")
    print("=" * 50)
    print(f"Location: {final_path}")
    print(f"Size: {size_gb:.2f} GB")
    print()
    print("You can now run: docker compose up --build")

except Exception as e:
    print(f"Error downloading model: {e}")
    print("\nAlternative: Download manually from:")
    print(f"https://huggingface.co/{repo_id}/blob/main/{filename}")
    exit(1)
