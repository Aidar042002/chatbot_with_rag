import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config.settings import VK_TOKEN
from infrastructure.store import create_data
from rag.pipeline import rag_pipeline
from rag.reranker import init_cross_encoder
from infrastructure.qdrant_storage import init_qdrant

async def init_data():
    init_qdrant()
    init_cross_encoder()
    # await create_data()
    print("Данные в бд загружены")

def send_message(user_id: int, text: str, vk):
    vk.messages.send(
        user_id=user_id,
        message=text[:4000],
        random_id=random.randint(1, 999999)
    )

async def chat_loop():
    await init_data()
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    greeted = set()

    print("Бот готов.")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            query = event.text.strip()

            if not query:
                continue

            if user_id not in greeted:
                greeted.add(user_id)
                send_message(user_id, "Привет! Я бот для консультирования. Задай вопрос или напиши /help", vk)

                if query == "/help":
                    send_message(user_id, "Просто задай свой вопрос о поступлении", vk)
                    continue

            print(f"\nВопрос: {query}")

            answer = await rag_pipeline(str(query))

            send_message(user_id, answer, vk)
            print(f"Ответ отправлен")