from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self):
        model_name:str = 'intfloat/multilingual-e5-small'
        self.model = SentenceTransformer(model_name)
        self.dimension = 384
        print(f"Модель embedder загружена.")

    def encode(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        embedding = self.model.encode(text)
        return embedding.tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

embedding_service = EmbeddingService()