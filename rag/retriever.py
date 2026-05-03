from typing import List
from models.document import Document
from repository.document_repository import DocumentRepository

async def get_context(query: str) -> List[Document]:
    similar = await DocumentRepository.find_similar_by_text(query)
    for i, doc in enumerate(similar):
        print(f"{i + 1}. {doc.text}...")
    return similar