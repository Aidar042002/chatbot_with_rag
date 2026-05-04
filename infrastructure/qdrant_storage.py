from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

_client, _collection_name = None, None

def initialize_client():
    global _client, _collection_name
    if _client is None or _collection_name is None:
        _client = QdrantClient(host="localhost", port=6333)
        _collection_name = "documents"

    return _client, _collection_name

def init_qdrant():
    client, collection_name = initialize_client()

    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print(f"Коллекция {collection_name} создана")
    else:
        print(f"Коллекция {collection_name} уже существует")