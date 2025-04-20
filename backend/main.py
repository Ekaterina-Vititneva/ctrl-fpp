from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from pydantic import BaseModel
from typing import List
from llm_loader import get_llm
import traceback
from dotenv import load_dotenv
import psycopg2

# Import your new page-based parser and chunker
from parser import parse_pdf_pages, chunk_pdf_pages
from embedding_model import get_embedding, get_embedding_with_metadata
#from rag import vectorstore
import pgvectorstore as vectorstore

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

UPLOAD_DIR = "data/docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# # class QueryRequest(BaseModel):
#     question: str

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
        print("✅ Uploaded:", filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 2. Parse & chunk the PDF into (page, chunk) dicts
    try:
        # parse each page individually
        parsed_pages = parse_pdf_pages(file_path)
        print("📄 Parsed", len(parsed_pages), "pages")
        # chunk them
        chunked_pages = chunk_pdf_pages(parsed_pages, chunk_size=300, overlap=50)
        print("✂️ Chunked into", len(chunked_pages), "chunks")

        if chunked_pages:
            print("🧠 First chunk:", chunked_pages[0])
        else:
            print("⚠️ No chunks found!")

        # Add 'source' to each chunk dict
        for chunk in chunked_pages:
            chunk["source"] = filename  # needed for metadata

        # Get embeddings and metadata
        embeddings, texts, sources, pages = get_embedding_with_metadata(chunked_pages)

        # Reconstruct proper chunk dicts for DB insertion
        chunk_dicts = [
            {"chunk": text, "source": source, "page": page}
            for text, source, page in zip(texts, sources, pages)
        ]


        # Save into pgvector DB
        # vectorstore.add_embeddings(embeddings, chunk_dicts, filename)
        try:
            vectorstore.add_embeddings(embeddings, chunk_dicts, filename)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


        # 5. Save index
        # vectorstore.save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing or embedding PDF: {str(e)}")

    return {"filename": filename, "message": "Upload + embedding successful!"}


# @app.post("/query")
# async def query_docs(req: QueryRequest):
#     """
#     Takes a user question, gets an embedding, searches FAISS,
#     and returns the top matching chunks (with page numbers).
#     """
#     q_embedding = get_embedding([req.question])[0]
#     results = vectorstore.search(q_embedding, top_k=3)
#     return {"question": req.question, "results": results}


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

        # 1) Vector search
        q_embedding = get_embedding([req.question])[0]
        results = vectorstore.search(q_embedding, top_k=3)

        # 2) Build context
        context = "\n\n".join([r["chunk"] for r in results])

        prompt = f"""
        You are a helpful assistant. Use the context to answer the question. Use markdown for the answer to structure it, if needed. 
        Context:
        {context}

        Question: {req.question}
        Answer:
        """

        # 3) Get LLM answer
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