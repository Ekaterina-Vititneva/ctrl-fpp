from __future__ import annotations

import math
import traceback
from parser import parse_pdf_pages, chunk_pdf_pages
from embedding_model import get_embedding_with_metadata
import pgvectorstore as vectorstore
from job_registry import jobs

# Granularity knobs
BATCH_SIZE       = 1         
PARSE_WEIGHT     = 0.10       # 0 – 0.30   of the bar
CHUNK_WEIGHT     = 0.05       # 0.30 – 0.35
EMBED_WEIGHT     = 0.80       # 0.35 – 0.95
STORE_WEIGHT     = 0.05       # 0.95 – 1.00

# Helper to map phase‑local progress (0‑1) → global bar (0‑1)
def _segment(base: float, span: float, frac: float) -> float:
    return round(base + span * frac, 3)


def process_pdf(job_id: str, filename: str, file_path: str) -> None:
    """
    Parse → chunk → embed → store, emitting fine‑grained progress so the
    front‑end bar moves continuously.
    Called via:   background_tasks.add_task(process_pdf, job_id, fname, path)
    """
    try:
        # ── 1. Parse pages ───────────────────────────────────────────────────
        pages = parse_pdf_pages(file_path)
        total_pages = len(pages)

        for idx, page in enumerate(pages, 1):
            jobs.update(
                job_id,
                state="parsing",
                phase=f"Seite {idx}/{total_pages}",
                progress=_segment(0.0, PARSE_WEIGHT, idx / total_pages),
            )

        # ── 2. Chunk pages ───────────────────────────────────────────────────
        # 2) Chunk pages – emit per‑page progress
        jobs.update(job_id, state="chunking")

        chunked_pages: list[dict] = []
        pages_done = 0
        for page_dict in pages:                       # pages is the list from parsing
            chunks = chunk_pdf_pages([page_dict], chunk_size=300, overlap=50)
            chunked_pages.extend(chunks)
            pages_done += 1

            # progress: 30 %→35 % of bar (CHUNK_WEIGHT = 0.05)
            frac = pages_done / len(pages)
            jobs.update(
                job_id,
                phase=f"Seite {pages_done}/{len(pages)}",
                progress=_segment(PARSE_WEIGHT, CHUNK_WEIGHT, frac),
            )
        
        total_chunks = len(chunked_pages)

        # ── 3. Embedding (batched) ───────────────────────────────────────────
        embeddings, chunk_dicts = [], []
        for done in range(0, total_chunks, BATCH_SIZE):
            batch = chunked_pages[done : done + BATCH_SIZE]
            for c in batch:
                c["source"] = filename

            e, t, s, p = get_embedding_with_metadata(batch)
            print(f"🧠 Embedding batch of {len(batch)} chunks → {len(e)} embeddings")

            embeddings.extend(e)
            chunk_dicts.extend(
                {"chunk": txt, "source": src, "page": pg}
                for txt, src, pg in zip(t, s, p)
            )

            done_chunks = min(done + BATCH_SIZE, total_chunks)
            jobs.update(
                job_id,
                state="embedding",
                phase=f"Chunk {done_chunks}/{total_chunks}",
                progress=_segment(
                    PARSE_WEIGHT + CHUNK_WEIGHT,
                    EMBED_WEIGHT,
                    done_chunks / total_chunks,
                ),
            )

        # ── 4. Store in Postgres ─────────────────────────────────────────────
        jobs.update(job_id, state="storing",
                    phase="Schreibe DB…",
                    progress=_segment(0.95, STORE_WEIGHT, 0.0))

        vectorstore.add_embeddings(embeddings, chunk_dicts, filename)

        # ── 5. Done ──────────────────────────────────────────────────────────
        jobs.update(job_id, state="done", phase=None, progress=1.0)

    except Exception as exc:
        traceback.print_exc()
        jobs.update(job_id, state="error", error=str(exc), progress=1.0)
# ───────────────────────────────────────────────────────────────────────────────
