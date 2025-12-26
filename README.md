# 🏥 Rx-Plain: AI Medical Report Interpreter

**Rx-Plain** is an intelligent medical assistant designed to bridge the gap between complex diagnostic reports and patient understanding. It combines advanced Computer Vision, Local RAG (Retrieval-Augmented Generation), and LLM interpretation to provide accurate, simplified case explanations.

---

## 🚀 How It Works

The system operates in three distinct modules, mirroring a cognitive process:

### 1. **The Eye (Vision Module)**
*   **Tech:** Google Gemini Vision (Flash model).
*   **Function:** Reads medical report images (e.g., blood tests, lab reports).
*   **Output:** Extracts structured data: Test Names, Result Values, Units, Reference Ranges, and flagged abnormalities.

### 2. **The Brain (Verification Module)**
*   **Tech:** LangChain + Ollama (Local LLM) + ChromaDB (Vector Store).
*   **Function:** Verifies the extracted data against official medical guidelines.
*   **Privacy:** Runs locally using **Ollama** and `nomic-embed-text` embeddings, ensuring no external leakage of RAG queries.
*   **Source:** Uses a library of official PDF guidelines stored in `medical_guidelines/`.

### 3. **The Interpreter (Explanation Module)**
*   **Tech:** Google Gemini (Generative AI).
*   **Function:** Synthesizes the patient data and verified guidelines.
*   **Output:** Generates a empathetic, plain-language explanation (e.g., in Hindi/English), explains "WHY" a result is abnormal, and suggests relevant questions for the doctor.

---

## ✨ Features

*   **📄 OCR Extraction:** Converts image-based reports into machine-readable text.
*   **🧠 Local Knowledge Base:** Uses verified medical documents (RAG) to ground answers, reducing hallucinations.
*   **🌍 Multi-Language Support:** Can explain reports in local languages (currently configured for Hindi).
*   **⚡ High Performance:** Uses `gemini-2.5-flash-lite` for speed and cost-efficiency.
*   **🔒 Privacy-First:** Vector embeddings and similarity search run locally.

---

## 🛠️ Installation & Setup

### Prerequisites
*   **Python 3.12+**
*   **Google API Key** (for Gemini)
*   **Ollama Installed** locally ([Download Ollama](https://ollama.com/))
    *   Pull the embedding model: `ollama pull nomic-embed-text`

### 1. Clone the Repository
```bash
git clone https://github.com/karanmourya/Rx-Plain
cd Rx-Plain
```

### 2. Install Dependencies
You can use `pip`:
```bash
pip install -r requirements.txt
```
*Note: This project uses `langchain-ollama`, `chromadb`, and `google-generativeai`.*

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

---

## 🏃 Usage Guide

### Step 1: Build the Knowledge Base ("The Brain")
Place your medical guideline PDFs inside the `medical_guidelines/` folder.
Then run:
```bash
python build_database.py
```
*This will ingest the PDFs, chunk them, and create a local Vector Store in `chroma_db/`.*

### Step 2: Run the Analyzer
Place your medical report image (e.g., `report.jpg`) in the project folder and update the filename in `main.py` if necessary.
Then run:
```bash
python main.py
```

### Output Example
The script will print:
1.  **[1] Extracted Raw Data** from the image.
2.  **[2] Verified Context** retrieved from your local RAG database.
3.  **[3] Final Explanation** in the target language.

---

## 🗺️ Future Roadmap

The project is currently a functional CLI prototype. Future plans include:

*   **💻 Web Interface:** A **Streamlit** dashboard (dependency already verified) for easy file uploads and user interaction.
*   **🔌 API Layer:** A **FastAPI** backend to serve mobile or web clients.
*   **📱 Mobile App:** Integration with frontend frameworks.
*   **🩺 Expanded KB:** Support for broader medical datasets beyond basic lab reports.

---

## ⚠️ Disclaimer
*Rx-Plain is an AI tool for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.*
