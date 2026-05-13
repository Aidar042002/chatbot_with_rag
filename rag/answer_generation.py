from typing import List
import requests
from models.document import Document
from config.settings import LM_STUDIO_URL, MODEL


def generate_answer(query: str, context_docs: List[Document], chat_history) -> str:
    if not context_docs:
        return "Не нашел информации по вашему вопросу."

    print(context_docs)

    best_doc = max(
        [doc for doc in context_docs if doc.source],
        key=lambda x: x.metadata.get("score", 0),
        default=None
    )

    prompt = f"""Вы помогаете отвечать на вопросы абитуриентов.
Отвечай кратко. Отвечай как официальное лицо, строго на основе предоставленного контекста.
Используй историю чата если она есть. 
Если информация отсутствует в контексте, скажи об этом честно.

КОНТЕКСТ:
{context_docs}

ВОПРОС: {query}

ИСТОРИЯ ЧАТА: {chat_history}

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
    if best_doc:
        answer += f"\n\nИсточник: {best_doc.source}"

    return answer.replace("#", "").replace("*", "").strip()