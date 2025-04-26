from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, shutil, pathlib
from pydantic import BaseModel
from typing import List
from llm_loader import get_llm
import traceback
from dotenv import load_dotenv
import psycopg2

# Import page-based parser and chunker
#from parser import parse_pdf_pages, chunk_pdf_pages
from embedding_model import get_embedding, get_embedding_with_metadata
#from rag import vectorstore
import pgvectorstore as vectorstore
from tasks import process_pdf
from job_registry import jobs

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
origins = os.getenv("FRONTEND_ORIGINS", "").split(",")
print("🔓 CORS allowed origins:", origins)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = pathlib.Path("data/docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hello from ctrl-fpp!"}

@app.post("/upload", status_code=202, response_model=None)
async def upload_file(    
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    1. Saves the uploaded PDF to disk.
    2. Registers a new JobRegistry entry → returns job_id immediately.
    3. Schedules background parsing/embedding.
    """
    # ----- basic validation ---------------------------------------------------
    fname = file.filename or "unnamed.pdf"
    if not fname.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    file_path = UPLOAD_DIR / fname
    # ----- persist the file ---------------------------------------------------
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(500, f"Could not write file: {exc}") from exc

    # ----- create a progress‑tracking job -------------------------------------
    job_id = jobs.create(fname)          # state = "queued", progress = 0.0

    # ----- hand off to background worker -------------------------------------
    background_tasks.add_task(process_pdf, job_id, fname, str(file_path))

    # ----- immediate 202 Accepted response ------------------------------------
    return JSONResponse(
        {
            "job_id": job_id,
            "filename": fname,
            "state": "queued",
            "message": "Upload accepted – embedding will start in the background."
        },
        status_code=202,
    )


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
        # structured_llm = llm.with_structured_output()

         # 1) Vector search part
        q_embedding = get_embedding([req.question])[0]

        # 2) Hybrid search in pgvectorstore
        results = vectorstore.hybrid_search(q_embedding, req.question, top_k=3)

        if not results:
            # fallback to pure vector search
            print("⚡ No keyword match, falling back to pure vector search")
            results = vectorstore.search(q_embedding, top_k=3)

        # 3) Build context
        context = "\n\n".join([r["chunk"] for r in results])

        prompt = f"""
        You are a helpful assistant answering questions based on provided document excerpts (context).
        Use ONLY the context below to answer the question. Do not make up information.
        If the context is insufficient, politely say you don't have enough information.
        Use clear and professional language.
        Format your answer very carefully in **Markdown**:
        - Use bullet points, headers, quotes if appropriate.
        - After every heading (e.g., #, ##), insert a blank line.
        - Highlight important terms in **bold** when helpful.

        Context:
        {context}

        Question: {req.question}

        Answer (in Markdown):
        """


        # 4) Get LLM answer
        answer_raw = llm.invoke(prompt)
        answer_text = answer_raw.content if hasattr(answer_raw, "content") else str(answer_raw)

        print("🔍 Query embedding:", q_embedding[:5], "...")
        #print("📄 Vectorstore has", len(vectorstore.doc_chunks), "chunks")
        cur = vectorstore.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        chunk_count = cur.fetchone()[0]
        print("📄 Vectorstore has", chunk_count, "chunks")


        for i, r in enumerate(results):
            print(f"🔗 {i+1}. {r['source']} (score: {r['distance']:.4f})")
            print("   ", r["chunk"][:80], "...")

        return {
            "question": req.question,
            "answer": answer_text,
            "sources": results
        }

    except Exception as e:
        print("⚠️ Error in /ask:")
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

@app.get("/documents")
def list_uploaded_documents():
    try:
        cur = vectorstore.conn.cursor()
        cur.execute("SELECT DISTINCT source FROM documents")
        rows = cur.fetchall()
        documents = [row[0] for row in rows]
        return JSONResponse(content={"documents": documents})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/test-db-write")
async def test_db_write():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()

        test_vector = [0.0] * 768
        cur.execute("""
            INSERT INTO documents (chunk, source, page, embedding)
            VALUES (%s, %s, %s, %s::vector)
        """, ("test", "test", 1, test_vector))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    
@app.get("/test-db-write-many")
async def test_db_write_many():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()

        test_vectors = []
        for i in range(50):
            test_vectors.append((
                f"test chunk {i+1}",
                "testfile.pdf",
                i + 1,
                [float(i % 10)] * 768
            ))

        cur.executemany("""
            INSERT INTO documents (chunk, source, page, embedding)
            VALUES (%s, %s, %s, %s::vector)
        """, test_vectors)
        conn.commit()
        return {"status": "success", "inserted": len(test_vectors)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

@app.get("/status/{job_id}")
def check_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job