import json
import asyncio
import pandas as pd

from rag.pipeline import rag_pipeline
from rag.retriever import get_context
from metrics import *
from rag.reranker import init_cross_encoder


async def evaluate():
    init_cross_encoder()
    with open("test_dataset.json", encoding="utf8") as f:
        dataset = json.load(f)

    results = []

    for item in dataset:
        question = item["question"]
        generate_answer = item["answer"]
        relevant_ids = item["relevant_doc_ids"]

        print(question)

        docs = await get_context(question)

        retrieved_ids = [doc.id for doc in docs]

        r5 = recall_at_k(relevant_ids, retrieved_ids, 5)
        p5 = precision_at_k(relevant_ids, retrieved_ids, 5)
        mrr_score = mrr(relevant_ids, retrieved_ids)
        ndcg = ndcg_at_k(relevant_ids, retrieved_ids, 5)

        generated = await rag_pipeline(question, [])

        results.append({
            "question": question,
            "gt_answer": generate_answer,
            "generated_answer": generated,
            "context": "\n".join([doc.text for doc in docs]),
            "recall@5": r5,
            "precision@5": p5,
            "mrr": mrr_score,
            "ndcg@5": ndcg
        })

    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False)

    print(df.mean(numeric_only=True))


if __name__ == "__main__":
    asyncio.run(evaluate())