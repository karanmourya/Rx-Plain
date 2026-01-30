import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import ollama
import os
import shutil
import uuid

app = FastAPI(title="Rx-Plain: Medical Report Interpreter")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

VISION_MODEL = "qwen3-vl:4b"
TEXT_MODEL = "qwen3-vl:4b"
EMBEDDING_MODEL = "nomic-embed-text"

os.makedirs("uploads", exist_ok=True)


def extract_text_from_image(image_path):
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()

        prompt = """
        You are a medical data extractor. 
        Analyze this image carefully.
        1. Extract all Test Names, Result Values, Units, and Reference Ranges.
        2. EXPLICITLY list any values that are flagged as High, Low, or Abnormal.
        3. If there is a diagnosis or impression section, transcribe it.
        Return the data in clear, plain text.
        """

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": prompt, "images": [img_data]}],
        )

        return response["message"]["content"]
    except Exception as e:
        return f"Error reading image: {e}"


def verify_with_rag(extracted_text):
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists("./chroma_db"):
        db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        results = db.similarity_search(extracted_text, k=3)
        verified_info = "\n".join([doc.page_content for doc in results])
        return verified_info
    else:
        return "Local database not found. Using general knowledge."


def generate_response(patient_data, medical_guidelines, language="English"):
    prompt = f"""
    You are 'Rx-Plain', a helpful medical assistant.
    
    PATIENT REPORT:
    {patient_data}
    
    OFFICIAL GUIDELINES (WHO/ICMR):
    {medical_guidelines}
    
    TASK:
    1. Explain the report results in simple {language}.
    2. If any result is abnormal, explain WHY using the Guidelines provided.
    3. Suggest 3 important questions to ask a doctor in {language}.
    
    TONE: Calm, professional, and empathetic.
    DISCLAIMER: Start with "I am an AI. Please consult a doctor."
    """

    try:
        response = ollama.chat(
            model=TEXT_MODEL, messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error generating response: {e}"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_report(file: UploadFile = File(...), language: str = "English"):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"uploads/{file_id}.{file_extension}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_data = extract_text_from_image(file_path)
        rag_context = verify_with_rag(extracted_data)
        final_response = generate_response(extracted_data, rag_context, language)

        os.remove(file_path)

        return {
            "success": True,
            "extracted_data": extracted_data,
            "rag_context": rag_context[:500] + "..."
            if len(rag_context) > 500
            else rag_context,
            "final_response": final_response,
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
