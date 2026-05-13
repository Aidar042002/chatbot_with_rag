import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config.settings import VK_TOKEN, ADMIN_PASSWORD, ADMIN_NAME
from rag.pipeline import rag_pipeline
from rag.reranker import init_cross_encoder
from infrastructure.qdrant_storage import init_qdrant
from services.admin_service import handle_admin_load_file, handle_admin_save_markdown_text, handle_admin_load_markdown

user_histories = {}
admin_sessions = {}

async def init_data():
    init_qdrant()
    init_cross_encoder()
    print("Данные в бд уже загружены")

def get_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Справка", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def send_message(user_id: int, text: str, vk, keyboard=None):
    params = {
        "user_id": user_id,
        "message": text[:4000],
        "random_id": random.randint(1, 999999)
    }
    if keyboard:
        params["keyboard"] = keyboard

    vk.messages.send(**params)


def send_snackbar_text(user_id: int, vk, is_admin_user: bool, is_authenticated: bool):
    if is_admin_user:
        if is_authenticated:
            message = ("Вы в режиме администратора.\n"
                       "Вы можете сохранить данные в базу знаний. Наберите цифру для нужного вам действия:\n"
                       "1 - загрузка файла pdf\n"
                       "2 - загрузка файла markdown\n"
                       "3 - загрузка текста\n"
                       " Для выхода напишите 'выйти'")
        else:
            message = "Вы админ. Введите пароль для входа в режим администратора"
    else:
        message = 'Задайте интересующий вас вопрос'

    vk.messages.send(user_id=user_id, message=message, random_id=random.randint(1, 999999))


async def chat_loop():
    await init_data()
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("Бот готов.")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            user = vk.users.get(user_ids=user_id)[0]

            query = event.text.strip()

            is_admin_user = (user['first_name'] == ADMIN_NAME)

            is_admin_mode = admin_sessions.get(user_id, False)

            if user_id not in admin_sessions:
                admin_sessions[user_id] = False

            if query.lower() == "начать":
                user_histories[user_id] = []
                welcome_text = "Нажмите на кнопку справка, если нужна помощь."
                send_message(user_id, welcome_text, vk, keyboard=get_keyboard())
                continue

            if query == "Справка":
                send_snackbar_text(user_id, vk, is_admin_user, is_admin_mode)
                continue

            print(f"\nВопрос: {query}")
            send_message(user_id, "Готовится ответ...", vk, keyboard=get_keyboard())

            if is_admin_user and not is_admin_mode:
                if query == ADMIN_PASSWORD:
                    admin_sessions[user_id] = True
                    send_message(user_id, "Пароль принят! Вы вошли в режим администратора.", vk,
                                 keyboard=get_keyboard())
                    send_message(
                        user_id,
                        "Вы в режиме администратора.\n"
                        "Вы можете сохранить данные в базу знаний. Наберите цифру для нужного вам действия:\n"
                        "1 - загрузка файла pdf\n"
                        "2 - загрузка файла markdown\n"
                        "3 - загрузка текста\n"
                        " Для выхода напишите 'выйти'",
                    vk, keyboard=get_keyboard())
                else:
                    if user_id not in user_histories:
                        user_histories[user_id] = []

                    # answer = 'Заглушка ответа'
                    answer = await rag_pipeline(str(query), user_histories[user_id])

                    user_histories[user_id].append(f"Пользователь: {query}")
                    user_histories[user_id].append(f"Бот: {answer}")

                    if len(user_histories[user_id]) > 10:
                        user_histories[user_id] = user_histories[user_id][-10:]

                    send_message(user_id, answer, vk, keyboard=get_keyboard())
                continue

            if is_admin_mode:
                if query.lower() == "выйти":
                    admin_sessions[user_id] = False
                    send_message(user_id,
                                 "Вы вышли из режима администратора. Теперь вы можете задавать обычные вопросы.",
                                 vk, keyboard=get_keyboard())
                    continue

                if query == "1":
                    send_message(user_id, "Переход в режим загрузки файлов pdf...", vk, keyboard=get_keyboard())
                    await handle_admin_load_file(user_id, vk, longpoll, get_keyboard())
                    send_message(user_id,
                                 "Вы в режиме администратора.\n"
                                 "Вы можете сохранить данные в базу знаний. Наберите цифру для нужного вам действия:\n"
                                 "1 - загрузка файла pdf\n"
                                 "2 - загрузка файла markdown\n"
                                 "3 - загрузка текста\n"
                                 " Для выхода напишите 'выйти'",
                                 vk, keyboard=get_keyboard())
                    continue
                elif query == "2":
                    send_message(user_id, "Переход в режим загрузки файлов markdown...", vk, keyboard=get_keyboard())
                    await handle_admin_load_markdown(user_id, vk, longpoll, get_keyboard())
                    continue
                elif query == "3":
                    send_message(user_id, "Переход в режим загрузки текста...", vk, keyboard=get_keyboard())
                    await handle_admin_save_markdown_text(user_id, vk, longpoll, get_keyboard())
                    continue
                else:
                    send_message(user_id, f"Неизвестная админ-команда: {query}\n"
                                          "Доступные команды:\n"
                                 "1 - загрузка файла pdf\n"
                                 "2 - загрузка файла markdown\n"
                                 "3 - загрузка текста\n"
                                 " Для выхода напишите 'выйти'",
                                 vk, keyboard=get_keyboard())
                continue

            if user_id not in user_histories:
                user_histories[user_id] = []

            # answer = 'Заглушка ответа'
            answer = await rag_pipeline(str(query), user_histories[user_id])

            user_histories[user_id].append(f"Пользователь: {query}")
            user_histories[user_id].append(f"Бот: {answer}")

            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]

            send_message(user_id, answer, vk, keyboard=get_keyboard())