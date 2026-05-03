import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config.settings import VK_TOKEN
from infrastructure.database import db
from infrastructure.store import create_data
from rag.pipeline import rag_pipeline
from rag.reranker import init_cross_encoder

async def init_data():
    await db.connect("postgresql://postgres:root@localhost/postgres")
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

    print("Бот готов.")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            query = event.text.strip()

            if not query:
                continue

            print(f"\nВопрос: {query}")

            answer = await rag_pipeline(str(query))

            send_message(user_id, answer, vk)
            print(f"Ответ отправлен")