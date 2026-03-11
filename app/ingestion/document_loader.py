from pathlib import Path
import fitz


def infer_metadata(path: Path) -> dict:
    """
    Infer metadata such as vendor name and document type
    from the file name.
    """

    file_name = path.name.lower()

    # -------------------------
    # Vendor detection
    # -------------------------
    vendor_name = "unknown"

    if "vendor_alpha" in file_name or "alpha" in file_name:
        vendor_name = "Vendor Alpha"

    elif "vendor_beta" in file_name or "beta" in file_name:
        vendor_name = "Vendor Beta"

    elif "vendor" in file_name:
        vendor_name = "Vendor Alpha"

    # -------------------------
    # Document type detection
    # -------------------------
    doc_type = "general"

    if "sla" in file_name:
        doc_type = "sla"

    elif "contract" in file_name:
        doc_type = "contract"

    elif "pricing" in file_name:
        doc_type = "pricing"

    elif "security" in file_name:
        doc_type = "security"

    elif "risk" in file_name:
        doc_type = "risk"

    return {
        "vendor_name": vendor_name,
        "doc_type": doc_type,
        "source_file": path.name,
    }


def load_document(file_path: str) -> tuple[str, dict]:
    """
    Load document text and infer metadata.

    Supports:
    - .txt
    - .pdf
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    metadata = infer_metadata(path)
    suffix = path.suffix.lower()

    # -------------------------
    # TXT loader
    # -------------------------
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8")
        return text, metadata

    # -------------------------
    # PDF loader
    # -------------------------
    if suffix == ".pdf":
        doc = fitz.open(file_path)
        pages = []

        for i, page in enumerate(doc):
            page_text = page.get_text().strip()
            if page_text:
                pages.append(f"[Page {i + 1}]\n{page_text}")

        text = "\n\n".join(pages)

        if not text.strip():
            raise ValueError(f"No readable text found in PDF: {file_path}")

        return text, metadata

    raise ValueError("Unsupported file type. Only .txt and .pdf are supported.")