import os
from typing import List
from langchain_core.documents import Document as LangChainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.document import Document
from repository.document_repository import DocumentRepository


def load_markdown_files(folder: str) -> List[LangChainDocument]:
    documents = []

    for file in os.listdir(folder):
        if file.endswith((".md", ".markdown")):
            path = os.path.join(folder, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            doc = LangChainDocument(
                page_content=content,
                metadata={"source": file}
            )
            documents.append(doc)
            print(f"Загружен: {file}")

    return documents


async def create_data():
    print("Загрузка документов...")
    docs = load_markdown_files("../data")

    if not docs:
        print("Нет .md файлов в папке data/")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"Создано {len(chunks)} фрагментов")

    qdrant_repo = DocumentRepository()

    for i, chunk in enumerate(chunks):
        doc1 = Document(
            pg_id=None,
            qdrant_id=None,
            text=chunk.page_content,
            metadata={"source": chunk.metadata.get("source", "unknown")}
        )

        created = await qdrant_repo.create(doc1)
        print(f"  Текст: {created}...")

    print(f"Всего сохранено {len(chunks)} фрагментов в Qdrant")