from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pydantic import BaseModel
from typing import List
from llm_loader import get_llm
from langchain.chains import RetrievalQA
import traceback
from dotenv import load_dotenv

from parser import parse_pdf, chunk_text
from embedding_model import get_embedding
from rag import vectorstore

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Hello from ctrl-fpp!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a PDF, parses & chunks it, embeds it, and adds to FAISS."""
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 1. Save the PDF
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Parse PDF
    try:
        pdf_text = parse_pdf(file_path)
        # 3. Chunk
        chunks = chunk_text(pdf_text, chunk_size=300, overlap=50)
        # 4. Embed
        embeddings = get_embedding(chunks)
        # 5. Add to vectorstore
        filenames = [filename] * len(chunks)
        vectorstore.add_embeddings(embeddings, chunks, filenames)
        # 6. Save index
        vectorstore.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing or embedding PDF: {str(e)}")

    return {"filename": filename, "message": "Upload + embedding successful!"}

@app.post("/query")
async def query_docs(req: QueryRequest):
    """
    Takes a user question, gets an embedding, searches FAISS,
    and returns the top matching chunks.
    """
    q_embedding = get_embedding([req.question])[0]
    results = vectorstore.search(q_embedding, top_k=3)
    return {"question": req.question, "results": results}

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_docs(req: AskRequest, request: Request):
    try:
        llm = get_llm()

        # Vector search
        q_embedding = get_embedding([req.question])[0]
        results = vectorstore.search(q_embedding, top_k=3)
        context = "\n\n".join([r["chunk"] for r in results])

        prompt = f"""
        You are a helpful assistant. Use the context to answer the question.
        Context:
        {context}

        Question: {req.question}
        Answer:
        """

        answer_raw = llm.invoke(prompt)
        answer_text = answer_raw.content if hasattr(answer_raw, "content") else str(answer_raw)

        print("🔍 Query embedding:", q_embedding[:5], "...")  # first few values
        print("📄 Vectorstore has", len(vectorstore.doc_chunks), "chunks")

        for i, r in enumerate(results):
            print(f"🔗 {i+1}. {r['source']} (score: {r['distance']:.4f})")
            print("   ", r["chunk"][:80], "...")  # first 80 chars


        return {
            "question": req.question,
            "answer": answer_text,
            "sources": results
        }

    except Exception as e:
        print("⚠️ Error in /askLocal:")
        traceback.print_exc()  # full trace to terminal
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_vectorstore():
    """
    Clears all stored vectors and deletes saved FAISS index files.
    """
    import shutil
    import os

    # Adjust this path if your FAISS index lives elsewhere
    vectorstore_dir = os.path.join("backend", "vectorstore")
    
    if os.path.exists(vectorstore_dir):
        shutil.rmtree(vectorstore_dir)
        os.makedirs(vectorstore_dir, exist_ok=True)

    # Optional: also clear in-memory vectorstore
    vectorstore.reset()  # <-- if your vectorstore object supports it
    return

@app.get("/status")
def status():
    return {"llm": os.getenv("LLM_PROVIDER", "openai"), "docs_loaded": len(vectorstore.doc_chunks)}
