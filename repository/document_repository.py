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

        payload = {
            "text": doc.text,
            "source": doc.metadata.get("source"),
            "document_name": doc.metadata.get("document_name")
        }

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
            Document(id=str(hit.id), text=hit.payload["text"], content=None, metadata={"source": hit.payload.get("source")})
            for hit in results.points
        ]

    @staticmethod
    async def get_all_document_names() -> list[str]:
        client, collection_name = initialize_client()

        try:
            result = client.scroll(
                collection_name=collection_name,
                with_payload=True,
                with_vectors=False,
                limit=10000
            )

            points = result[0]

            document_names = set()

            for point in points:
                payload = point.payload or {}

                document_name = payload.get("document_name")

                if document_name:
                    document_names.add(document_name)

            return sorted(list(document_names))

        except Exception as e:
            print(f"Ошибка получения списка документов: {e}")
            return []

    @staticmethod
    async def delete_by_document_name(document_name: str) -> str:
        try:
            client, collection_name = initialize_client()

            if not document_name or not document_name.strip():
                return "Ошибка удаления: пустое имя файла"

            document_name = document_name.strip()

            client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_name",
                                match=models.MatchValue(value=document_name)
                            )
                        ]
                    )
                )
            )

            print(f"Удалён документ: {document_name}")
            return f"Удалён документ: {document_name}"

        except Exception as e:
            print(f"Ошибка удаления: {e}")
            return "Ошибка удаления"