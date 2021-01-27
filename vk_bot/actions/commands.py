from vkbottle.bot import Message
from tools import keyboards


async def start(ans: Message, chat_id: int, storage):
    """Команда бота Начать"""
    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Привет\n')
    await ans.answer('Для начала пройдите небольшую регистрацию😉\n')
    await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))


async def registration(ans: Message, chat_id: int, storage):
    """Команда бота Регистрация"""
    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Повторная регистрация😉\n')
    await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))
