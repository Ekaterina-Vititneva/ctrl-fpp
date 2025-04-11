import fitz  # PyMuPDF
import re
from typing import List

def parse_pdf(pdf_path: str) -> str:
    """
    Reads the PDF from pdf_path and returns the entire text as a single string.
    """
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        text = page.get_text("text")
        full_text.append(text)
    doc.close()
    return "\n".join(full_text)

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Splits the text into overlapping chunks of size `chunk_size`.
    Overlap ensures some context continuity between chunks.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        # Rejoin into a string
        chunk_str = " ".join(chunk)
        chunks.append(chunk_str)
        start += chunk_size - overlap
    return chunks
