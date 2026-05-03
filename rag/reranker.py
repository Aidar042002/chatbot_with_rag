from typing import List
from models.document import Document
from sentence_transformers import CrossEncoder

_reranker = None

def init_cross_encoder():
    global _reranker
    if _reranker is None:
        _reranker =  CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("Reranker загружен")
    return _reranker

async def rerank_documents(query: str, docs: List[Document], top_n: int = 3) -> List[Document]:
    global _reranker
    if not docs:
        return []

    pairs = [(query, doc.text[:500]) for doc in docs]
    scores = _reranker.predict(pairs)

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    top_docs = [doc for doc, _ in ranked[:top_n]]

    print(f"Ретривер: {len(docs)} \n. Реранкер: {len(top_docs)}")
    return top_docs