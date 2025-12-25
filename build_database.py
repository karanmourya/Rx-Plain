import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings # <--- NEW LIBRARY
from langchain_chroma import Chroma 
from langchain_chroma import Chroma

def create_database():
    # 0. Clean up old DB if it exists to prevent conflicts
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")

    # 1. Load PDFs
    pdf_folder_path = "./medical_guidelines"
    documents = []

    print("Loading PDFs...")
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)
        print(f"Error: Folder '{pdf_folder_path}' not found.")
        return

    files = [f for f in os.listdir(pdf_folder_path) if f.endswith('.pdf')]
    if not files:
        print("No PDFs found.")
        return

    for file in files:
        print(f" - Processing {file}...")
        loader = PyPDFLoader(os.path.join(pdf_folder_path, file))
        documents.extend(loader.load())

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    doc_splits = text_splitter.split_documents(documents)
    print(f"Split documents into {len(doc_splits)} chunks.")

    # 3. Create Vector Store using OLLAMA
    print("Creating Local Database with Ollama (nomic-embed-text)...")
    
    # This runs locally on your GPU/CPU - No API Limits!
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vector_store = Chroma.from_documents(
        documents=doc_splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print("Success! Database created in './chroma_db' folder.")

if __name__ == "__main__":
    create_database()