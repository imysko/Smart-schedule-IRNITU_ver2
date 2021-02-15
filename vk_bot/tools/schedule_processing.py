from vkbottle.bot import Message

from tools import keyboards


async def sending_schedule(ans: Message, schedule_str: str):
    """Отправка расписания пользователю"""
    for schedule in schedule_str:
        await ans.answer(f'{schedule}')


async def sending_schedule_is_not_available(ans: Message):
    await ans.answer('Расписание временно недоступно🚫😣\n'
                     'Попробуйте позже⏱', keyboard=keyboards.make_keyboard_start_menu())


async def sending_service_is_not_available(ans: Message):
    await ans.answer('Сервис временно недоступен🚫😣\n'
                     'Попробуйте позже⏱', keyboard=keyboards.make_keyboard_start_menu())
