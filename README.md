# Rx-Plain

AI-powered medical report interpreter that runs 100% locally. Upload a photo of a lab report and get a plain-language explanation — no API keys, no data leaves your machine.

## How It Works

The system uses a three-stage pipeline:

```
Image Upload → [1] Vision OCR → [2] RAG Verification → [3] Plain Language Explanation
```

**Stage 1 — The Eye (OCR)**
Qwen3-VL reads the report image and extracts test names, values, units, reference ranges, and flagged abnormalities.

**Stage 2 — The Brain (RAG)**
The extracted data is cross-referenced against medical guideline PDFs stored in a local ChromaDB vector database, using `nomic-embed-text` embeddings.

**Stage 3 — The Interpreter**
Qwen3-VL synthesizes the patient data with verified guidelines and generates an empathetic, easy-to-understand explanation — including what abnormal results mean and what to ask your doctor.

## Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) installed and running

Pull the required models:

```bash
ollama pull qwen3-vl:4b
ollama pull nomic-embed-text:latest
```

Verify they're installed:

```bash
uv run python check_models.py
```

## Installation

```bash
git clone https://github.com/karanmourya/Rx-Plain
cd Rx-Plain
uv sync
```

## Setup — Build the Knowledge Base

1. Place medical guideline PDFs inside `medical_guidelines/`
2. Build the vector database:

```bash
uv run python build_database.py
```

This ingests the PDFs, chunks them, and creates a local ChromaDB store in `chroma_db/`.

## Usage

### Web Interface (recommended)

```bash
uv run python app.py
```

Open http://localhost:8000 — drag and drop a report image, choose a language, and get results.

Features:
- Drag & drop file upload
- Language selection (English / Hindi)
- Real-time streaming progress
- Three result cards: Extracted Data, Medical Guidelines, AI Explanation

### CLI

```bash
uv run python main.py
```

Edit the `image_file` variable in `main.py` to point to your report image.

## Project Structure

```
rx-plain/
├── app.py                  # FastAPI web server
├── main.py                 # CLI interface
├── build_database.py       # PDF → ChromaDB vector store builder
├── check_models.py         # Ollama model verification script
├── medical_guidelines/     # Place your reference PDFs here
├── example_reports/        # Sample reports for testing
├── templates/
│   └── index.html          # Web UI template
├── static/
│   ├── style.css           # UI styles
│   └── script.js           # Client-side logic with SSE streaming
├── chroma_db/              # Generated vector store (gitignored)
└── uploads/                # Temporary upload storage (gitignored)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Vision / OCR | Qwen3-VL (4B) via Ollama |
| Text Generation | Qwen3-VL (4B) / smollm2 via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Vector Store | ChromaDB |
| Orchestration | LangChain |
| Web Framework | FastAPI + Uvicorn |
| Package Manager | uv |

## Example Reports

The `example_reports/` folder includes sample images and PDFs for testing:

| File | Type |
|------|------|
| `blood-test-report.jpg` | Blood test report |
| `diabetes-lab-report.pdf` | Diabetes lab report |
| `doctor-handwritten-report.jpg` | Handwritten doctor notes |
| `gallstones-report.jpg` | Gallstones imaging report |
| `generic-lab-report.jpg` | General lab report |
| `malaria-lab-report-1.png` | Malaria lab report (image) |
| `malaria-lab-report-2.pdf` | Malaria lab report (PDF) |
| `prescription-handwritten.png` | Handwritten prescription |

## Disclaimer

Rx-Plain is an AI tool for educational and informational purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
