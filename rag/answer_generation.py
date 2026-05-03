from typing import List
from gigachat import GigaChat
from config.settings import GIGA_TOKEN
from models.document import Document


def llm_init():
    giga = GigaChat(credentials=GIGA_TOKEN, verify_ssl_certs=False)
    return giga

def generate_answer(query: str,  context_docs: List[Document]) -> str:
    giga = llm_init()

    if not context_docs:
        return "Не нашел информации по вашему вопросу."

    print(context_docs)

    prompt = f"""Ты помощник по вопросам для абитуриентов. Ответь на вопрос, используя только контекст ниже.

КОНТЕКСТ:
{context_docs}

ВОПРОС: {query}

ОТВЕТ:"""

    response = giga.chat(prompt)
    answer = response.choices[0].message.content

    return f"{answer}"