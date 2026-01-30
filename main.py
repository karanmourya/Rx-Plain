import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import ollama
import os

from dotenv import load_dotenv

load_dotenv()

VISION_MODEL = "qwen3-vl:4b"
TEXT_MODEL = "qwen3-vl:4b"
EMBEDDING_MODEL = "nomic-embed-text"


def check_ollama_models():
    print("\nChecking Ollama models...")
    try:
        models = ollama.list()
        available_models = [m["name"] for m in models["models"]]

        required_models = [VISION_MODEL, TEXT_MODEL, EMBEDDING_MODEL]
        for model in required_models:
            if model in available_models:
                print(f"✓ {model} available")
            else:
                print(f"✗ {model} NOT found. Run: ollama pull {model}")
    except Exception as e:
        print(f"Error checking Ollama: {e}")


def extract_text_from_image(image_path):
    print(f"\n[1] Analyzing Image: {image_path}...")

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
    print("\n[2] Verifying with Local Knowledge Base...")

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists("./chroma_db"):
        db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

        results = db.similarity_search(extracted_text, k=3)
        verified_info = "\n".join([doc.page_content for doc in results])
        return verified_info
    else:
        return "Local database not found. Using general knowledge."


def generate_response(patient_data, medical_guidelines, language="Hindi"):
    print(f"\n[3] Generating {language} Explanation...")

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


if __name__ == "__main__":
    check_ollama_models()

    image_file = "malaria lab report.png"

    if os.path.exists(image_file):
        raw_text = extract_text_from_image(image_file)
        if "Error" in raw_text:
            print(raw_text)
        else:
            print(f"--- Extracted Data ---\n{raw_text[:200]}...\n")

            context = verify_with_rag(raw_text)
            print(f"--- Verified Guidelines ---\n{context[:200]}...\n")

            final_output = generate_response(raw_text, context, language="Hindi")

            print("=" * 50)
            print(final_output)
            print("=" * 50)
    else:
        print(
            f"Error: '{image_file}' not found. Please add a dummy medical report image to the folder."
        )
