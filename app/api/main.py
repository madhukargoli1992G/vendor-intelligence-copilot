from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File

from app.core.llm import llm
from app.ingestion.ingest_pipeline import ingest_document
from app.rag.rag_pipeline import ask_question
from app.rag.vector_store import recreate_collection

app = FastAPI(
    title="Vendor Intelligence Copilot",
    description="AI-powered vendor analysis system using RAG",
    version="1.0.0",
)

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Vendor Intelligence Copilot API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-llm")
def test_llm():
    response = llm.invoke("Explain what a vendor SLA is in one sentence.")
    return {"response": response.content}


@app.post("/reset-collection")
def reset_collection():
    try:
        recreate_collection()
        return {
            "status": "reset",
            "collection": "vendor_docs",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
def ingest(file_path: str):
    try:
        result = ingest_document(file_path)
        return {
            "status": "ingested",
            "chunks": result["chunks"],
            "metadata": result["metadata"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest-upload")
async def ingest_upload(file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename).suffix.lower()

        if suffix not in [".txt", ".pdf"]:
            raise HTTPException(
                status_code=400,
                detail="Only .txt and .pdf files are supported.",
            )

        save_path = RAW_DATA_DIR / file.filename

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        result = ingest_document(str(save_path))

        return {
            "status": "uploaded_and_ingested",
            "saved_to": str(save_path),
            "chunks": result["chunks"],
            "metadata": result["metadata"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask")
def ask(
    question: str,
    vendor_name: Optional[str] = None,
    doc_type: Optional[str] = None,
):
    try:
        return ask_question(
            question=question,
            vendor_name=vendor_name,
            doc_type=doc_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))