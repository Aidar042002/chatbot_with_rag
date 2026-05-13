import os
from typing import List, Optional
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
        chunk_size=1500,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    print(f"Создано {len(chunks)} фрагментов")

    qdrant_repo = DocumentRepository()

    for i, chunk in enumerate(chunks):
        doc1 = Document(
            id=None,
            text=chunk.page_content,
            metadata={"source": chunk.metadata.get("source", "unknown")}
        )

        created = await qdrant_repo.create(doc1)
        print(f"  Текст: {created}...")

    print(f"Всего сохранено {len(chunks)} фрагментов в Qdrant")


async def load_one_file(file_path: str, source: Optional[str] = None):
    print(f"Загрузка файла: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )

    doc = LangChainDocument(page_content=content, metadata={"source": file_path})
    chunks = splitter.split_documents([doc])

    print(f"Создано {len(chunks)} фрагментов")

    qdrant_repo = DocumentRepository()
    for chunk in chunks:
        doc1 = Document(
            id=None,
            text=chunk.page_content,
            metadata={"source": chunk.metadata.get("source", "unknown")},
            source=source
        )
        await qdrant_repo.create(doc1)

    print(f"Загружено {len(chunks)} фрагментов в Qdrant")

