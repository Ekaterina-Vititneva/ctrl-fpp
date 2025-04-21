# backend/tasks.py
from parser import parse_pdf_pages, chunk_pdf_pages
from embedding_model import get_embedding_with_metadata
import pgvectorstore as vectorstore
from job_registry import jobs
import traceback, math

BATCH_SIZE  = 64
PROG_STEPS  = 20

def process_pdf(job_id: str, filename: str, file_path: str):
    """Parse → chunk → embed → store while updating JobRegistry."""
    try:
        # 1) Parse pages
        jobs.update(job_id, state="parsing", progress=0.0)
        parsed_pages = parse_pdf_pages(file_path)
        print("📄 Parsed", len(parsed_pages), "pages")

        # 2) Chunk pages
        jobs.update(job_id, state="chunking")
        chunked_pages = chunk_pdf_pages(parsed_pages, chunk_size=300, overlap=50)
        print("✂️ Chunked into", len(chunked_pages), "chunks")

        # 3) Embeddings (batched)
        total = len(chunked_pages)
        jobs.update(job_id, state="embedding", total=total, progress=0.0)

        embeddings, texts, sources, pages = [], [], [], []
        batches = math.ceil(total / BATCH_SIZE)

        for b in range(batches):
            start = b * BATCH_SIZE
            batch = chunked_pages[start : start + BATCH_SIZE]

            for c in batch:
                c["source"] = filename

            e, t, s, p = get_embedding_with_metadata(batch)
            embeddings.extend(e); texts.extend(t); sources.extend(s); pages.extend(p)

            if (b + 1) % max(1, batches // PROG_STEPS) == 0 or b == batches - 1:
                prog = round((start + len(batch)) / total, 3)
                jobs.update(job_id, progress=prog)

        # 4) Store in pgvector
        jobs.update(job_id, state="storing", progress=0.98)
        chunk_dicts = [
            {"chunk": txt, "source": src, "page": pg}
            for txt, src, pg in zip(texts, sources, pages)
        ]
        vectorstore.add_embeddings(embeddings, chunk_dicts, filename)
        print("✅ Embeddings stored in DB")

        jobs.update(job_id, state="done", progress=1.0)

    except Exception:
        traceback.print_exc()
        jobs.update(job_id, state="error", progress=1.0)
