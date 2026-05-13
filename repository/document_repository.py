from models.document import Document
from rag.embedding import embedding_service
import uuid
from infrastructure.qdrant_storage import initialize_client
from qdrant_client import models

class DocumentRepository:
    @staticmethod
    async def create(doc: Document) -> Document:
        client, collection_name = initialize_client()

        vector = doc.content
        if vector is None and doc.text:
            vector = embedding_service.encode(doc.text)

        if not doc.id:
            doc.id = str(uuid.uuid4())

        payload = {"text": doc.text}
        if doc.source:
            payload["source"] = doc.source

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=doc.id,
                    vector={
                        "dense": vector,
                        "sparse": models.Document(
                            text=doc.text,
                            model="Qdrant/bm25",
                        ),
                    },
                    payload=payload,
                )
            ]
        )

        return doc


    @staticmethod
    async def find_similar_by_text(query_text: str, limit: int = 10) -> list[Document]:
        client, collection_name = initialize_client()

        dense_vector = embedding_service.encode(query_text)

        results = client.query_points(
            collection_name=collection_name,
            prefetch=[
                models.Prefetch(
                    query=models.Document(
                        text=query_text,
                        model="Qdrant/bm25",
                    ),
                    using="sparse",
                    limit=limit,
                ),
                models.Prefetch(
                    query=dense_vector,
                    using="dense",
                    limit=limit,
                )
            ],
            query=models.FusionQuery(fusion=models.Fusion.DBSF),
            limit=limit,
        )

        return [
            Document(id=str(hit.id), text=hit.payload["text"], content=None, source=hit.payload.get("source"))
            for hit in results.points
        ]