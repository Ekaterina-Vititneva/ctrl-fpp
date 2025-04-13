from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pydantic import BaseModel
from typing import List
from llm_loader import get_llm
import traceback
from dotenv import load_dotenv

# Import your new page-based parser and chunker
from parser import parse_pdf_pages, chunk_pdf_pages
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
    """Uploads a PDF, parses & chunks it by page, embeds it, and adds to FAISS with page info."""
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 1. Save the PDF
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Parse & chunk the PDF into (page, chunk) dicts
    try:
        # parse each page individually
        parsed_pages = parse_pdf_pages(file_path)
        # chunk them
        chunked_pages = chunk_pdf_pages(parsed_pages, chunk_size=300, overlap=50)

        # 3. Prepare embeddings
        # We only need the 'chunk' text for embedding
        chunk_texts = [cp["chunk"] for cp in chunked_pages]
        embeddings = get_embedding(chunk_texts)

        # 4. Add to vectorstore
        # Our rag.py expects:
        #    add_embeddings(embeddings: List[List[float]], chunk_dicts: List[Dict], filename: str)
        # so we can store {"text", "source", "page"} in doc_chunks.
        vectorstore.add_embeddings(embeddings, chunked_pages, filename)

        # 5. Save index
        vectorstore.save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing or embedding PDF: {str(e)}")

    return {"filename": filename, "message": "Upload + embedding successful!"}


@app.post("/query")
async def query_docs(req: QueryRequest):
    """
    Takes a user question, gets an embedding, searches FAISS,
    and returns the top matching chunks (with page numbers).
    """
    q_embedding = get_embedding([req.question])[0]
    results = vectorstore.search(q_embedding, top_k=3)
    return {"question": req.question, "results": results}


class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_docs(req: AskRequest, request: Request):
    """
    Takes a user question, retrieves top chunks (with page numbers),
    builds a prompt, calls LLM to form an answer, returns the final answer + sources.
    """
    try:
        llm = get_llm()

        # 1) Vector search
        q_embedding = get_embedding([req.question])[0]
        results = vectorstore.search(q_embedding, top_k=3)

        # 2) Build context
        context = "\n\n".join([r["chunk"] for r in results])

        prompt = f"""
        You are a helpful assistant. Use the context to answer the question.
        Context:
        {context}

        Question: {req.question}
        Answer:
        """

        # 3) Get LLM answer
        answer_raw = llm.invoke(prompt)
        answer_text = answer_raw.content if hasattr(answer_raw, "content") else str(answer_raw)

        print("🔍 Query embedding:", q_embedding[:5], "...")
        print("📄 Vectorstore has", len(vectorstore.doc_chunks), "chunks")

        for i, r in enumerate(results):
            print(f"🔗 {i+1}. {r['source']} (score: {r['distance']:.4f})")
            print("   ", r["chunk"][:80], "...")

        return {
            "question": req.question,
            "answer": answer_text,
            "sources": results
        }

    except Exception as e:
        print("⚠️ Error in /askLocal:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_vectorstore():
    """
    Clears all stored vectors and deletes saved FAISS index files.
    """
    import shutil
    vectorstore_dir = os.path.join("backend", "vectorstore")

    if os.path.exists(vectorstore_dir):
        shutil.rmtree(vectorstore_dir)
        os.makedirs(vectorstore_dir, exist_ok=True)

    vectorstore.reset()
    return


@app.get("/status")
def status():
    return {
        "llm": os.getenv("LLM_PROVIDER", "openai"),
        "docs_loaded": len(vectorstore.doc_chunks)
    }
