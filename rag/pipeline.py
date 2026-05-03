from typing import List

from models.document import Document
from rag.answer_generation import generate_answer
from rag.retriever import get_context
from rag.reranker import rerank_documents

async def rag_pipeline(query:str):
    context: List[Document] = await get_context(query)
    reranked_context: List[Document] = await rerank_documents(query, context)
    answer = generate_answer(query, reranked_context)

    return answer