import math


def recall_at_k(relevant, retrieved, k):
    retrieved_k = retrieved[:k]
    return len(set(relevant) & set(retrieved_k)) / len(relevant)


def precision_at_k(relevant, retrieved, k):
    retrieved_k = retrieved[:k]
    return len(set(relevant) & set(retrieved_k)) / k


def mrr(relevant, retrieved):
    for i, doc_id in enumerate(retrieved):
        if doc_id in relevant:
            return 1 / (i + 1)
    return 0


def dcg(relevant, retrieved, k):
    score = 0
    for i, doc_id in enumerate(retrieved[:k]):
        rel = 1 if doc_id in relevant else 0
        score += rel / math.log2(i + 2)
    return score


def ndcg_at_k(relevant, retrieved, k):
    ideal = dcg(relevant, relevant, k)
    actual = dcg(relevant, retrieved, k)

    if ideal == 0:
        return 0

    return actual / ideal