from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pydantic import BaseModel
from typing import List
from llm_loader import get_local_llm
from langchain.chains import RetrievalQA
import traceback

from parser import parse_pdf, chunk_text
from embedding_model import get_embedding
from rag import vectorstore

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
        vectorstore.add_embeddings(embeddings, chunks)
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

@app.post("/askLocal")
async def ask_docs_local(req: AskRequest, request: Request):
    try:
        llm = get_local_llm()

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

        answer = llm.invoke(prompt)

        return {
            "question": req.question,
            "answer": answer,
            "sources": results
        }

    except Exception as e:
        print("⚠️ Error in /askLocal:")
        traceback.print_exc()  # full trace to terminal
        raise HTTPException(status_code=500, detail=str(e))
