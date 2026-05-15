from typing import List
from models.document import Document
from sentence_transformers import CrossEncoder

_reranker = None

def init_cross_encoder():
    global _reranker
    if _reranker is None:
        _reranker =  CrossEncoder('DiTy/cross-encoder-russian-msmarco', max_length=512)
        print("Reranker загружен")
    return _reranker

async def rerank_documents(query: str, docs: List[Document], top_n: int = 5) -> List[Document]:
    global _reranker
    if not docs:
        return []

    pairs = [(query, doc.text) for doc in docs]
    scores = _reranker.predict(pairs)

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    top_docs = []
    for doc, score in ranked[:top_n]:
        doc.metadata = doc.metadata or {}
        doc.metadata["score"] = float(score)
        top_docs.append(doc)

    print("\nПосле rerank:")
    for i, (doc, score) in enumerate(ranked[:top_n], 1):
        print(f"{i}. ID={doc.id} | score={score:.4f} | {doc.source} |{doc.text[:100]}")

    return top_docs