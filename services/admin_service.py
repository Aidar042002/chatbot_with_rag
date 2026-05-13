import time

import requests
import random, os

from infrastructure.convert import pdf_to_md
from vk_api.longpoll import VkEventType
from infrastructure.store import load_one_file

def send_message(user_id: int, text: str, vk, keyboard=None):
    params = {
        "user_id": user_id,
        "message": text[:4000],
        "random_id": random.randint(1, 999999)
    }

    if keyboard:
        params["keyboard"] = keyboard

    vk.messages.send(**params)


async def save_file_pdf(event, vk, type, source: None):
    if not event.attachments:
        return False

    print(event.attachments)

    if event.attachments.get('attach1_type') != 'doc':
        return False

    message = vk.messages.getById(
        message_ids=event.message_id
    )

    print(message)

    attachments = message['items'][0]['attachments']

    if not attachments:
        return False

    doc = attachments[0]['doc']
    file_url = doc['url']
    file_name = doc['title']

    data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_folder, exist_ok=True)

    file_path = os.path.join(data_folder, file_name)

    response = requests.get(file_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

    print(f"Файл сохранён: {file_path}")


    if file_name.lower().endswith('.pdf'):
        print("Обнаружен PDF, конвертируем в Markdown...")
        md_file = pdf_to_md(file_path, data_folder)
        if md_file:
            print(f"PDF сконвертирован в MD: {md_file}")
            os.remove(file_path)
            await load_one_file(md_file, source)

    return True

async def save_markdown_file(event, vk, source: str):
    if not event.attachments:
        return False

    print(event.attachments)

    if event.attachments.get('attach1_type') != 'doc':
        return False

    message = vk.messages.getById(
        message_ids=event.message_id
    )

    print(message)

    attachments = message['items'][0]['attachments']

    if not attachments:
        return False

    doc = attachments[0]['doc']
    file_url = doc['url']
    file_name = doc['title']

    if not file_name.lower().endswith('.md'):
        print(f"Файл {file_name} не является Markdown файлом")
        return False

    data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_folder, exist_ok=True)

    file_path = os.path.join(data_folder, file_name)

    response = requests.get(file_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

    print(f"Markdown файл сохранён: {file_path}")

    await load_one_file(file_path, source)

    return True

async def handle_admin_load_file(user_id, vk, longpoll, original_keyboard):
    send_message(user_id, "Введите источник документа, например, ссылку. Если источника нет, введите «-»", vk, keyboard=original_keyboard)

    source = None
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()
            if source:
                send_message(user_id, f"Источник принят: '{source}'\nТеперь отправьте файл (PDF документ):", vk,
                             keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Источник не может быть пустым. Введите источник:", vk,
                             keyboard=original_keyboard)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            if event.attachments:
                if source == '-':
                    source = None
                saved_file = await save_file_pdf(event, vk, 'pdf', source)

                if saved_file:
                    send_message(user_id, f"Файл успешно загружен!\n", vk,
                                 keyboard=original_keyboard)
                else:
                    send_message(user_id, "Ошибка при загрузке файла. Попробуйте ещё раз.", vk,
                                 keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Файл не обнаружен. Пожалуйста, отправьте PDF документ:", vk,
                             keyboard=original_keyboard)

async def handle_admin_load_markdown(user_id, vk, longpoll, original_keyboard):
    send_message(user_id, "Введите источник документа, например, ссылку. Если источника нет, введите «-»", vk, keyboard=original_keyboard)

    source = None
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()
            if source:
                send_message(user_id, f"Описание принято: '{source}'\nТеперь отправьте Markdown файл (.md):", vk,
                             keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Описание не может быть пустым. Введите описание:", vk,
                             keyboard=original_keyboard)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            if event.attachments:
                if source == '-':
                    source = None
                print(f"Загрузка Markdown документа с описанием: {source}")
                saved_file = await save_markdown_file(event, vk, source)

                if saved_file:
                    send_message(user_id, f"Markdown файл успешно загружен!\n", vk,
                                 keyboard=original_keyboard)
                else:
                    send_message(user_id, "Ошибка при загрузке файла. Убедитесь, что файл имеет расширение .md", vk,
                                 keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Файл не обнаружен. Пожалуйста, отправьте Markdown файл (.md):", vk,
                             keyboard=original_keyboard)


async def save_markdown_text(event, vk, source: str, text: str):
    if not text or not text.strip():
        return False

    print(f"Сохранение Markdown текста с описанием: {source}")

    data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_folder, exist_ok=True)

    safe_filename = str(int(time.time()))

    file_name = f"{safe_filename}.md"
    file_path = os.path.join(data_folder, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Markdown текст сохранён в файл: {file_path}")

    await load_one_file(file_path, source)

    return True


async def handle_admin_save_markdown_text(user_id, vk, longpoll, original_keyboard):
    send_message(user_id, "Введите источник документа, например, ссылку. Если источника нет, введите «-»", vk, keyboard=original_keyboard)

    source = None
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()
            if source:
                send_message(user_id,
                             f"Источник принят: '{source}'\nТеперь введите текст документа:",
                             vk,
                             keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Источник не может быть пустым. Введите источник:", vk,
                             keyboard=original_keyboard)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            markdown_text = event.text.strip()

            if markdown_text:
                if source == '-':
                    source = None
                saved = await save_markdown_text(event, vk, source, markdown_text)

                if saved:
                    send_message(user_id,
                                 f"Текст успешно сохранён!\n",
                                 vk,
                                 keyboard=original_keyboard)
                else:
                    send_message(user_id, "Ошибка при сохранении текста. Попробуйте ещё раз.", vk,
                                 keyboard=original_keyboard)
                break
            else:
                send_message(user_id, "Текст не может быть пустым. Введите текст документа:", vk,
                             keyboard=original_keyboard)