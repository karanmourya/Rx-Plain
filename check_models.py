import ollama

print("Checking available Ollama models...")

try:
    models = ollama.list()
    print(f"\nTotal models installed: {len(models['models'])}\n")

    recommended_models = {
        "qwen3-vl:4b": "Vision + Text (Recommended for OCR and generation)",
        "nomic-embed-text:latest": "Embeddings (Required for RAG)",
        "smollm2:latest": "Fast text generation (Optional)",
        "qwen2.5-coder:latest": "Code model (Optional)",
    }

    available_models = [m["name"] for m in models["models"]]

    for model in recommended_models:
        if model in available_models:
            print(f"✓ {model} - {recommended_models[model]}")
        else:
            print(f"✗ {model} - NOT FOUND. Run: ollama pull {model}")

    print("\nAll installed models:")
    for m in models["models"]:
        print(f"  - {m['name']} ({m.get('size', 0) / 1024**3:.2f} GB)")

except Exception as e:
    print(f"Error checking Ollama: {e}")
    print("\nMake sure Ollama is running:")
    print("  1. Download: https://ollama.com/")
    print("  2. Start Ollama application")
    print("  3. Run: ollama list")
