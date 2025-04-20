from sentence_transformers import SentenceTransformer
from typing import List, Dict
import torch

# Load local embedding model
# e5-small-v2 for semantic search
# model_name = "intfloat/e5-small-v2"
model_name = "sentence-transformers/all-mpnet-base-v2"
embedding_model = SentenceTransformer(model_name)

def get_embedding(texts: List[str]) -> List[List[float]]:
    """
    Returns a list of embeddings for the input texts using the local E5 model.
    Each embedding is a list of floats (vector).
    """
    with torch.no_grad():
        embeddings = embedding_model.encode(texts, show_progress_bar=False)
    # Convert NumPy arrays to Python lists
    return [emb.tolist() for emb in embeddings]

def get_embedding_with_metadata(chunks: List[Dict]) -> (List[List[float]], List[str], List[str], List[int]):
    """
    Returns embeddings and extracted metadata from text chunks.

    Each chunk in chunks must be a dict with keys: 'text', 'source', 'page'
    Returns a tuple of:
    - embeddings: list of vectors
    - texts: list of chunk strings
    - sources: list of filenames
    - pages: list of page numbers
    """
    texts = [c["chunk"] for c in chunks]
    sources = [c["source"] for c in chunks]
    pages = [c["page"] for c in chunks]
    embeddings = get_embedding(texts)
    return embeddings, texts, sources, pages
