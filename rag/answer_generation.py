from typing import List
import requests
from models.document import Document
from config.settings import LM_STUDIO_URL, MODEL


def generate_answer(query: str, context_docs: List[Document]) -> str:

    if not context_docs:
        return "Не нашел информации по вашему вопросу."

    prompt = f"""Ты помогаешь отвечать на вопросы абитуриентов. 
Отвечай строго на основе предоставленного контекста. 
Если информация отсутствует в контексте, скажи об этом честно.

КОНТЕКСТ:
{context_docs}

ВОПРОС: {query}

ОТВЕТ:"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()

    answer = response.json()["choices"][0]["message"]["content"]

    return answer.replace("#", "").replace("*", "").strip()