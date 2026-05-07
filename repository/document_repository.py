from qdrant_client.models import PointStruct
from models.document import Document
from rag.embedding import embedding_service
import uuid
from infrastructure.qdrant_storage import initialize_client

class DocumentRepository:
    @staticmethod
    async def create(doc: Document) -> Document:
        client, collection_name = initialize_client()

        vector = doc.content
        if vector is None and doc.text:
            vector = embedding_service.encode(doc.text)

        if not doc.id:
            doc.id = str(uuid.uuid4())

        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=doc.id,
                    vector=vector,
                    payload={
                        "text": doc.text,
                    }
                )
            ]
        )

        return doc

    @staticmethod
    async def find_similar_by_text(query_text: str, limit: int = 5) -> list[Document]:
        client, collection_name = initialize_client()

        query_vector = embedding_service.encode(query_text)

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        )

        documents = []
        for hit in results.points:
            doc = Document(
                id=hit.id,
                text=hit.payload["text"],
                content=hit.vector if hasattr(hit, 'vector') else None,
            )
            documents.append(doc)

        return documents