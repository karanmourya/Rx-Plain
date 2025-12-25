import warnings
# Suppress the annoying deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import google.generativeai as genai
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import PIL.Image
import os

from dotenv import load_dotenv

load_dotenv()

# --- SETUP ---
# Get key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=GOOGLE_API_KEY)

# --- CONFIGURATION ---
# We use Flash for the hackathon (Faster + No 404 errors)
MODEL_NAME = 'gemini-2.5-flash-lite' 

# --- MODULE 1: THE EYE (Gemini Vision) ---
def extract_text_from_image(image_path):
    print(f"\n[1] Analyzing Image: {image_path}...")
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        img = PIL.Image.open(image_path)
        
        prompt = """
        You are a medical data extractor. 
        Analyze this image carefully.
        1. Extract all Test Names, Result Values, Units, and Reference Ranges.
        2. EXPLICITLY list any values that are flagged as High, Low, or Abnormal.
        3. If there is a diagnosis or impression section, transcribe it.
        Return the data in clear, plain text.
        """
        
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"Error reading image: {e}"

# --- MODULE 2: THE BRAIN (Local Ollama RAG) ---
def verify_with_rag(extracted_text):
    print("\n[2] Verifying with Local Knowledge Base...")
    
    # Using the local Ollama model we set up
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Connect to the local DB
    if os.path.exists("./chroma_db"):
        db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        
        # Search for relevant guidelines
        results = db.similarity_search(extracted_text, k=3)
        verified_info = "\n".join([doc.page_content for doc in results])
        return verified_info
    else:
        return "Local database not found. Using general knowledge."

# --- MODULE 3: THE INTERPRETER (Gemini Text) ---
def generate_response(patient_data, medical_guidelines, language="Hindi"):
    print(f"\n[3] Generating {language} Explanation...")
    model = genai.GenerativeModel(MODEL_NAME)
    
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
    
    response = model.generate_content(prompt)
    return response.text

# --- RUN THE APP ---
if __name__ == "__main__":
    image_file = "mum_stone_report.jpeg" 
    
    if os.path.exists(image_file):
        # 1. Vision
        raw_text = extract_text_from_image(image_file)
        if "Error" in raw_text:
            print(raw_text)
        else:
            print(f"--- Extracted Data ---\n{raw_text[:200]}...\n")
            
            # 2. RAG
            context = verify_with_rag(raw_text)
            print(f"--- Verified Guidelines ---\n{context[:200]}...\n")
            
            # 3. Generation
            final_output = generate_response(raw_text, context, language="Hindi")
            
            print("="*50)
            print(final_output)
            print("="*50)
    else:
        print(f"Error: '{image_file}' not found. Please add a dummy medical report image to the folder.")