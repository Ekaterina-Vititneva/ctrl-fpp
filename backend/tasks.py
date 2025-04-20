from parser import parse_pdf_pages, chunk_pdf_pages
from embedding_model import get_embedding_with_metadata
import pgvectorstore as vectorstore
import traceback

def process_pdf(filename: str, file_path: str):
    try:
        parsed_pages = parse_pdf_pages(file_path)
        print("📄 Parsed", len(parsed_pages), "pages")

        chunked_pages = chunk_pdf_pages(parsed_pages, chunk_size=300, overlap=50)
        print("✂️ Chunked into", len(chunked_pages), "chunks")

        if chunked_pages:
            print("🧠 First chunk:", chunked_pages[0])
        else:
            print("⚠️ No chunks found!")

        for chunk in chunked_pages:
            chunk["source"] = filename

        embeddings, texts, sources, pages = get_embedding_with_metadata(chunked_pages)

        chunk_dicts = [
            {"chunk": text, "source": source, "page": page}
            for text, source, page in zip(texts, sources, pages)
        ]

        vectorstore.add_embeddings(embeddings, chunk_dicts, filename)
        print("✅ Embeddings stored in DB")

    except Exception as e:
        print("❌ Error during PDF processing:")
        traceback.print_exc()
