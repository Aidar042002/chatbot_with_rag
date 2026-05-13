from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

model = SentenceTransformer("intfloat/multilingual-e5-small")

def embed(text, is_query=False):
    text = str(text)

    if is_query:
        text = "query: " + text
    else:
        text = "passage: " + text

    return model.encode([text])


def cosine(a, b):
    return cosine_similarity(a, b)[0][0]


def evaluate():
    df = pd.read_csv("results.csv")

    faithfulness_scores = []
    correctness_scores = []

    for _, row in df.iterrows():

        ans_emb = embed(row["generated_answer"])
        ctx_emb = embed(row["context"])

        faith = cosine(ans_emb, ctx_emb)

        gt_emb = embed(row["gt_answer"])

        corr = cosine(ans_emb, gt_emb)

        faithfulness_scores.append(faith)
        correctness_scores.append(corr)

    print("\nGeneration metrics (E5):")
    print(f"Faithfulness: {np.mean(faithfulness_scores):.4f}")
    print(f"Answer Correctness: {np.mean(correctness_scores):.4f}")


if __name__ == "__main__":
    evaluate()