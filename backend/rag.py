import faiss
import os
import pickle
from typing import List, Dict

# Store the FAISS index and the associated metadata in vectorstore/
INDEX_PATH = "vectorstore/index.faiss"
DOCSTORE_PATH = "vectorstore/docstore.pkl"

class VectorStore:
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize a flat L2 FAISS index with dimension = embedding_dim.
        Default dimension for e5-small-v2 is 384.
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.doc_chunks = []  # In-memory store for chunk text
        self.ids = []         # IDs for each chunk

    def add_embeddings(self, embeddings: List[List[float]], chunks: List[str]):
        """
        Add new embeddings to the FAISS index, keep track of chunk text in memory.
        """
        import numpy as np
        vecs = np.array(embeddings).astype('float32')
        start_id = len(self.ids)
        ids_range = range(start_id, start_id + len(vecs))

        # Add to FAISS
        self.index.add(vecs)

        # Save metadata in memory
        for i, c in zip(ids_range, chunks):
            self.ids.append(i)
            self.doc_chunks.append(c)

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Search the index using the given query embedding, return top_k results.
        """
        import numpy as np
        q = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(q, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            chunk_text = self.doc_chunks[idx]
            results.append({"chunk": chunk_text, "distance": float(dist)})
        return results

    def save(self):
        """
        Save FAISS index plus chunk metadata (docstore) to disk.
        """
        # Save index
        faiss.write_index(self.index, INDEX_PATH)

        # Save chunk data (docstore)
        with open(DOCSTORE_PATH, "wb") as f:
            pickle.dump({
                "doc_chunks": self.doc_chunks,
                "ids": self.ids
            }, f)

    def load(self):
        """
        Load FAISS index and docstore if they exist.
        """
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)

        if os.path.exists(DOCSTORE_PATH):
            with open(DOCSTORE_PATH, "rb") as f:
                data = pickle.load(f)
                self.doc_chunks = data["doc_chunks"]
                self.ids = data["ids"]


# Initialize a global instance so we can reuse across endpoints
vectorstore = VectorStore()
vectorstore.load()
