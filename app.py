import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import ollama
import os
import shutil
import uuid
import json

app = FastAPI(title="Rx-Plain: Medical Report Interpreter")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

VISION_MODEL = "qwen3-vl:4b"
TEXT_MODEL = "smollm2:latest"
EMBEDDING_MODEL = "nomic-embed-text"

os.makedirs("uploads", exist_ok=True)


def extract_text_from_image(image_path):
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()

        prompt = """Extract all test names, values, units, and reference ranges. List any flagged abnormalities (High/Low). If diagnosis section exists, transcribe it."""

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
        results = db.similarity_search(extracted_text, k=1)
        verified_info = (
            results[0].page_content if results else "No relevant guidelines found."
        )
        return verified_info
    else:
        return "Local database not found. Using general knowledge."


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

        prompt = f"""You are Rx-Plain AI. DISCLAIMER: I am an AI. Please consult a doctor.

Report: {extracted_data}
Guidelines: {rag_context}

Explain in {language}:
1. What the results mean
2. Why any values are abnormal
3. 3 questions to ask your doctor

Keep it simple and empathetic."""

        response = ollama.chat(
            model=TEXT_MODEL, messages=[{"role": "user", "content": prompt}]
        )
        final_response = response["message"]["content"]

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


@app.post("/analyze-stream")
async def analyze_report_stream(
    file: UploadFile = File(...), language: str = "English"
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"uploads/{file_id}.{file_extension}"

    async def generate():
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            yield f"data: {json.dumps({'step': 'extracting', 'message': 'Extracting text from image...'})}\n\n"

            extracted_data = extract_text_from_image(file_path)
            yield f"data: {json.dumps({'step': 'extracted', 'data': extracted_data})}\n\n"

            yield f"data: {json.dumps({'step': 'rag', 'message': 'Searching medical guidelines...'})}\n\n"
            rag_context = verify_with_rag(extracted_data)
            yield f"data: {json.dumps({'step': 'rag_done', 'data': rag_context[:500] + '...' if len(rag_context) > 500 else rag_context})}\n\n"

            yield f"data: {json.dumps({'step': 'generating', 'message': 'Generating explanation...'})}\n\n"

            prompt = f"""You are Rx-Plain AI. DISCLAIMER: I am an AI. Please consult a doctor.

Report: {extracted_data}
Guidelines: {rag_context}

Explain in {language}:
1. What the results mean
2. Why any values are abnormal
3. 3 questions to ask your doctor

Keep it simple and empathetic."""

            response = ollama.chat(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )

            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    yield f"data: {json.dumps({'step': 'streaming', 'content': chunk['message']['content']})}\n\n"

            os.remove(file_path)
            yield f"data: {json.dumps({'step': 'done'})}\n\n"

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
