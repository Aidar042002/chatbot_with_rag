from typing import List
import requests
from requests import RequestException
from models.document import Document
from config.settings import LM_STUDIO_URL, MODEL


def generate_answer(query: str, context_docs: List[Document], chat_history) -> str:
    if not context_docs:
        return "Не нашел информации по вашему вопросу."

    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        source = doc.metadata.get("source")
        part = f" {doc.text}"
        if source:
            part += f"\nИсточник: {source}"
        context_parts.append(part)

    context_text = "\n\n".join(context_parts)
    print(f"""Context:\n{context_text}""")

    prompt = f"""Вы помощник для консультирования для абитуриентов,
     который отвечает на вопросы строго на основе предоставленных документов.
     Правила:
     - Отвечай кратко и по существу
     - Используй только информацию из документов ниже
     - Если информации нет — честно скажи об этом
     - В конце ответа одной строкой укажи все источники которые есть в документах. Если источников нет — ничего не пиши про него.

ДОКУМЕНТЫ:
{context_text}

ИСТОРИЯ ДИАЛОГА:
{chat_history if chat_history else "Нет"}

ВОПРОС: {query}

ОТВЕТ:"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        return answer.replace("#", "").replace("*", "").strip()

    except RequestException as e:
        print(f"Ошибка запроса к LLM: {e}")
        return "Сервис временно недоступен. Попробуйте позже."

    except KeyError as e:
        print(f"Некорректный ответ от LLM: {e}")
        return "Модель вернула некорректный ответ."

    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return "Сервис временно недоступен. Попробуйте позже"