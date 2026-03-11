from app.ingestion.document_loader import load_document
from app.ingestion.chunker import chunk_text
from app.rag.vector_store import get_vector_store


def ingest_document(file_path: str) -> dict:
    text, metadata = load_document(file_path)
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No text chunks were created from the document.")

    vector_store = get_vector_store()

    metadatas = []
    for i, _ in enumerate(chunks):
        metadatas.append(
            {
                **metadata,
                "chunk_id": i + 1,
            }
        )

    vector_store.add_texts(
        texts=chunks,
        metadatas=metadatas,
    )

    return {
        "chunks": len(chunks),
        "metadata": metadata,
    }