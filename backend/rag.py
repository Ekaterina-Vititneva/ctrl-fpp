import faiss
from langchain_community.vectorstores import FAISS
import os
import pickle
from typing import List, Dict
from embedding_model import get_embedding

# Storing the FAISS index and the associated metadata in vectorstore/
VECTORSTORE_DIR = "vectorstore"
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "index.faiss")
DOCSTORE_PATH = os.path.join(VECTORSTORE_DIR, "docstore.pkl")

class VectorStore:
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize a flat L2 FAISS index with dimension = embedding_dim.
        Default dimension for e5-small-v2 is 384.
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.doc_chunks = []  # Stores dicts: {"text": chunk, "source": filename, "page": page_num}
        self.ids = []

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        chunk_dicts: List[Dict],  # each with {"page": int, "chunk": str}
        filename: str
    ):
        """
        Instead of separate 'chunks' and 'filenames' arrays,
        we pass chunk_dicts that contain page and chunk data,
        plus a single filename for them all.
        """
        import numpy as np
        vecs = np.array(embeddings).astype('float32')
        start_id = len(self.ids)
        ids_range = range(start_id, start_id + len(vecs))

        self.index.add(vecs)

        for i, (chunk_obj) in zip(ids_range, chunk_dicts):
            page_num = chunk_obj["page"]
            text = chunk_obj["chunk"]
            self.ids.append(i)
            self.doc_chunks.append({
                "text": text,
                "source": filename,
                "page": page_num
            })


    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Search the index using the given query embedding, return top_k results.
        Each result includes the chunk text, source filename, page number, and similarity distance.
        """
        import numpy as np
        q = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(q, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            chunk_obj = self.doc_chunks[idx]
            results.append({
                "chunk": chunk_obj["text"],
                "source": chunk_obj["source"],
                "page": chunk_obj["page"],
                "distance": float(dist)
                })

        return results

    def save(self):
        """
        Save FAISS index plus chunk metadata (docstore) to disk.
        """
        os.makedirs(VECTORSTORE_DIR, exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

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

    def reset(self):
        """
        Delete all saved data and reinitialize empty in-memory state.
        """
        import shutil

        if os.path.exists(VECTORSTORE_DIR):
            shutil.rmtree(VECTORSTORE_DIR)

        os.makedirs(VECTORSTORE_DIR, exist_ok=True)

        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.doc_chunks = []
        self.ids = []

# Initialize a global instance so we can reuse across endpoints
vectorstore = VectorStore()
vectorstore.load()
