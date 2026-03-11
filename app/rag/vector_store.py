from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

from app.core.embeddings import embeddings
from app.core.qdrant_client import client
from app.core.config import COLLECTION_NAME


def recreate_collection() -> None:
    collections = client.get_collections().collections
    existing_names = [collection.name for collection in collections]

    if COLLECTION_NAME in existing_names:
        client.delete_collection(collection_name=COLLECTION_NAME)

    vector_size = len(embeddings.embed_query("test embedding"))

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def ensure_collection() -> None:
    collections = client.get_collections().collections
    existing_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in existing_names:
        vector_size = len(embeddings.embed_query("test embedding"))

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


def get_vector_store() -> QdrantVectorStore:
    ensure_collection()
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )