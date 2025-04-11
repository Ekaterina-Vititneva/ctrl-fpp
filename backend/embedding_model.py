from sentence_transformers import SentenceTransformer
from typing import List
import torch

# Load local embedding model
# e5-small-v2 for semantic search
model_name = "intfloat/e5-small-v2"
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
