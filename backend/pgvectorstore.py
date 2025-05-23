import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

if not DB_URL:

    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Connect and register the vector extension
conn = psycopg2.connect(DB_URL)
register_vector(conn)
cur = conn.cursor()

# Ensure the table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    chunk TEXT,
    source TEXT,
    page INTEGER,
    embedding VECTOR(384)
)
""")
conn.commit()

def reset():
    with psycopg2.connect(DB_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents")
            conn.commit()


def add_embeddings(embeddings, chunk_dicts, filename):
    print("📥 Inserting", len(embeddings), "embeddings into DB")

    values = []
    for emb, chunk in zip(embeddings, chunk_dicts):
        try:
            values.append((chunk["chunk"], chunk["source"], chunk.get("page", 0), emb))
        except Exception as e:
            print("⚠️ Error in chunk dict:", chunk)
            print("❌", str(e))

    if values:
        try:
            execute_values(cur,
                "INSERT INTO documents (chunk, source, page, embedding) VALUES %s",
                values
            )
            conn.commit()
            print("✅ DB insert complete")
        except Exception as e:
            print("❌ DB insert error:", str(e))
    else:
        print("⚠️ No values to insert!")


def search(query_embedding, top_k=3):
    cur.execute("""
        SELECT chunk, source, page, embedding <#> %s::vector AS distance
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))
    rows = cur.fetchall()
    return [
        {
            "chunk": r[0],
            "source": r[1],
            "page": r[2],
            "distance": r[3]
        }
        for r in rows
    ]

def hybrid_search(query_embedding, query_text, top_k=3):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT chunk, source, page,
                (0.7 * (1 - (embedding <=> %s::vector)) + 0.3 * ts_rank_cd(to_tsvector('german', chunk), plainto_tsquery('german', %s))) AS hybrid_score
            FROM documents
            WHERE to_tsvector('german', chunk) @@ plainto_tsquery('german', %s)
            ORDER BY hybrid_score DESC
            LIMIT %s
            """,
            (query_embedding, query_text, query_text, top_k)
        )
        rows = cur.fetchall()
        return [
            {"chunk": r[0], "source": r[1], "page": r[2], "score": r[3]}
            for r in rows
        ]