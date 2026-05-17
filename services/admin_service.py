import time
import requests
import random
import os

from infrastructure.convert import pdf_to_md
from vk_api.longpoll import VkEventType
from infrastructure.store import load_one_file
from repository.document_repository import DocumentRepository

def send_message(user_id: int, text: str, vk, keyboard=None):
    params = {
        "user_id": user_id,
        "message": text[:4000],
        "random_id": random.randint(1, 999999)
    }

    if keyboard:
        params["keyboard"] = keyboard

    vk.messages.send(**params)


async def save_file_pdf(event, vk, file_type, source: str, document_name: str):
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

    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data'
    )
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
            await load_one_file(md_file, document_name, source)

    return True


async def save_markdown_file(event, vk, source: str, document_name: str):
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

    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data'
    )
    os.makedirs(data_folder, exist_ok=True)

    file_path = os.path.join(data_folder, file_name)

    response = requests.get(file_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

    print(f"Markdown файл сохранён: {file_path}")

    await load_one_file(file_path, document_name, source)

    return True


async def save_markdown_text(event, vk, source: str, text: str, document_name: str):
    if not text or not text.strip():
        return False

    print(f"Сохранение Markdown текста с описанием: {source}")

    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data'
    )
    os.makedirs(data_folder, exist_ok=True)

    safe_filename = str(int(time.time()))
    file_name = f"{safe_filename}.md"
    file_path = os.path.join(data_folder, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Markdown текст сохранён в файл: {file_path}")

    await load_one_file(file_path, document_name, source)

    return True


async def handle_admin_load_file(user_id, vk, longpoll, original_keyboard):
    send_message(
        user_id,
        "Введите источник документа, например ссылку. Если источника нет, введите «-»",
        vk,
        keyboard=original_keyboard
    )

    source = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()

            if source:
                break
            else:
                send_message(
                    user_id,
                    "Источник не может быть пустым. Введите источник:",
                    vk,
                    keyboard=original_keyboard
                )

    send_message(
        user_id,
        "Введите имя документа:",
        vk,
        keyboard=original_keyboard
    )

    document_name = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            document_name = event.text.strip()

            if document_name:
                send_message(
                    user_id,
                    f"Имя документа: '{document_name}'\nТеперь отправьте PDF документ:",
                    vk,
                    keyboard=original_keyboard
                )
                break
            else:
                send_message(
                    user_id,
                    "Имя документа не может быть пустым.",
                    vk,
                    keyboard=original_keyboard
                )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            if event.attachments:
                if source == '-':
                    source = None

                saved_file = await save_file_pdf(
                    event,
                    vk,
                    'pdf',
                    source,
                    document_name
                )

                if saved_file:
                    send_message(
                        user_id,
                        "Файл успешно загружен!",
                        vk,
                        keyboard=original_keyboard
                    )
                else:
                    send_message(
                        user_id,
                        "Ошибка при загрузке файла. Попробуйте ещё раз.",
                        vk,
                        keyboard=original_keyboard
                    )
                break
            else:
                send_message(
                    user_id,
                    "Файл не обнаружен. Пожалуйста, отправьте PDF документ:",
                    vk,
                    keyboard=original_keyboard
                )


async def handle_admin_load_markdown(user_id, vk, longpoll, original_keyboard):
    send_message(
        user_id,
        "Введите источник документа, например ссылку. Если источника нет, введите «-»",
        vk,
        keyboard=original_keyboard
    )

    source = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()

            if source:
                break
            else:
                send_message(
                    user_id,
                    "Источник не может быть пустым.",
                    vk,
                    keyboard=original_keyboard
                )

    send_message(
        user_id,
        "Введите имя документа:",
        vk,
        keyboard=original_keyboard
    )

    document_name = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            document_name = event.text.strip()

            if document_name:
                send_message(
                    user_id,
                    f"Имя документа: '{document_name}'\nТеперь отправьте Markdown файл (.md):",
                    vk,
                    keyboard=original_keyboard
                )
                break
            else:
                send_message(
                    user_id,
                    "Имя документа не может быть пустым.",
                    vk,
                    keyboard=original_keyboard
                )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            if event.attachments:
                if source == '-':
                    source = None

                saved_file = await save_markdown_file(
                    event,
                    vk,
                    source,
                    document_name
                )

                if saved_file:
                    send_message(
                        user_id,
                        "Markdown файл успешно загружен!",
                        vk,
                        keyboard=original_keyboard
                    )
                else:
                    send_message(
                        user_id,
                        "Ошибка при загрузке файла. Убедитесь, что файл имеет расширение .md",
                        vk,
                        keyboard=original_keyboard
                    )
                break
            else:
                send_message(
                    user_id,
                    "Файл не обнаружен. Пожалуйста, отправьте Markdown файл (.md):",
                    vk,
                    keyboard=original_keyboard
                )


async def handle_admin_save_markdown_text(user_id, vk, longpoll, original_keyboard):
    send_message(
        user_id,
        "Введите источник документа, например ссылку. Если источника нет, введите «-»",
        vk,
        keyboard=original_keyboard
    )

    source = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            source = event.text.strip()

            if source:
                break
            else:
                send_message(
                    user_id,
                    "Источник не может быть пустым.",
                    vk,
                    keyboard=original_keyboard
                )

    send_message(
        user_id,
        "Введите имя документа:",
        vk,
        keyboard=original_keyboard
    )

    document_name = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            document_name = event.text.strip()

            if document_name:
                send_message(
                    user_id,
                    f"Имя документа: '{document_name}'\nТеперь введите текст документа:",
                    vk,
                    keyboard=original_keyboard
                )
                break
            else:
                send_message(
                    user_id,
                    "Имя документа не может быть пустым.",
                    vk,
                    keyboard=original_keyboard
                )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            markdown_text = event.text.strip()

            if markdown_text:
                if source == '-':
                    source = None

                saved = await save_markdown_text(
                    event,
                    vk,
                    source,
                    markdown_text,
                    document_name
                )

                if saved:
                    send_message(
                        user_id,
                        "Текст успешно сохранён!",
                        vk,
                        keyboard=original_keyboard
                    )
                else:
                    send_message(
                        user_id,
                        "Ошибка при сохранении текста. Попробуйте ещё раз.",
                        vk,
                        keyboard=original_keyboard
                    )
                break
            else:
                send_message(
                    user_id,
                    "Текст не может быть пустым. Введите текст документа:",
                    vk,
                    keyboard=original_keyboard
                )

async def get_documents_with_names():
    try:
        names = await DocumentRepository.get_all_document_names()

        names = [name for name in names if name and name.strip()]
        names = sorted(set(names))

        return "\n".join(f"{i + 1} {name}" for i, name in enumerate(names))

    except Exception as e:
        print(f"Ошибка при получении списка документов: {e}")
        return []

async def delete_documents_with_names(document_name:str):
        return await DocumentRepository.delete_by_document_name(document_name)