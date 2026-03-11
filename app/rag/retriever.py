from typing import Optional
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.rag.vector_store import get_vector_store


def build_filter(
    vendor_name: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> Optional[Filter]:
    conditions = []

    if vendor_name:
        conditions.append(
            FieldCondition(
                key="metadata.vendor_name",
                match=MatchValue(value=vendor_name),
            )
        )

    if doc_type:
        conditions.append(
            FieldCondition(
                key="metadata.doc_type",
                match=MatchValue(value=doc_type),
            )
        )

    if not conditions:
        return None

    return Filter(must=conditions)


def retrieve_context(
    query: str,
    k: int = 3,
    vendor_name: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> list[dict]:
    vector_store = get_vector_store()
    query_filter = build_filter(vendor_name=vendor_name, doc_type=doc_type)

    docs = vector_store.similarity_search(
        query=query,
        k=k,
        filter=query_filter,
    )

    results = []
    for doc in docs:
        results.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
        )

    return results