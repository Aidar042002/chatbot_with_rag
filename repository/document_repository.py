import json
from typing import List

from infrastructure.database import db
from models.document import Document
from rag.embedding import embedding_service


class DocumentRepository:

    @staticmethod
    async def create(doc: Document) -> Document:
        vector = doc.content
        if vector is None and doc.text:
            vector = embedding_service.encode(doc.text)

        vector_str = str(vector)

        metadata_str = json.dumps(doc.metadata) if doc.metadata else "{}"

        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO documents (text, content, metadata) VALUES ($1, $2::vector, $3::jsonb) RETURNING id",
                doc.text, vector_str, metadata_str
            )
            doc.id = row["id"]
            return doc

    @staticmethod
    async def find_similar_by_text(query_text: str, limit: int = 5) -> List[Document]:
        query_vector = embedding_service.encode(query_text)
        query_vector_str = str(query_vector)

        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id,
                       text,
                       metadata,
                       1 - (content <=> $1::vector) as similarity
                FROM documents
                WHERE content IS NOT NULL
                ORDER BY content <=> $1::vector
                    LIMIT $2
                """,
                query_vector_str, limit
            )
            return [
                Document(id=r["id"], text=r["text"], metadata=r["metadata"] if r["metadata"] else {})
                for r in rows
            ]
