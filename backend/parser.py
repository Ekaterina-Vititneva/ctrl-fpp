import fitz  # PyMuPDF
from typing import List, Dict

def parse_pdf_pages(pdf_path: str) -> List[Dict]:
    """
    Reads the PDF from pdf_path and returns a list of dicts,
    where each dict is: {"page": page_num, "text": page_text}.
    """
    doc = fitz.open(pdf_path)
    parsed_pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        # Store both text and page number
        parsed_pages.append({"page": page_num, "text": text})

    doc.close()
    return parsed_pages

def chunk_pdf_pages(parsed_pages: List[Dict], chunk_size=300, overlap=50) -> List[Dict]:
    """
    For each page dict, chunk the text, preserving page info.
    Returns a list of dicts: {"page": int, "chunk": str}
    """
    chunks_output = []

    for page_dict in parsed_pages:
        page_num = page_dict["page"]
        text = page_dict["text"]
        # Split into words
        words = text.split()
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_str = " ".join(chunk_words)
            chunks_output.append({"page": page_num, "chunk": chunk_str})
            # Move start forward
            start += chunk_size - overlap

    return chunks_output
