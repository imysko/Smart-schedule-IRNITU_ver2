from datetime import datetime
from tools.storage import MongodbService

from API.functions_api import find_week, APIError
from API.functions_api import full_schedule_in_str, full_schedule_in_str_prep, \
    get_one_day_schedule_in_str_prep, get_one_day_schedule_in_str, get_next_day_schedule_in_str, \
    get_next_day_schedule_in_str_prep, schedule_view_exams
from API.functions_api import get_near_lesson, get_now_lesson, get_now_lesson_in_str_stud, get_now_lesson_in_str_prep
from tools import keyboards, statistics, schedule_processing



storage = MongodbService().get_instance()


def groups_exam(group):
    schedule = storage.get_schedule_exam(group=group)
    del schedule['_id']
    clear_list = []
    for i in range(len(schedule['exams']['exams'])):
        if schedule['exams']['exams'][i] not in clear_list:
            clear_list.append(schedule['exams']['exams'][i])
    schedule['exams']['exams'] = clear_list
    return schedule



def get_schedule(bot, message, storage, tz):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user.get('group'):
        bot.send_message(chat_id=chat_id, text='Выберите период\n',
                         reply_markup=keyboards.make_keyboard_choose_schedule())
        statistics.add(action='Расписание', storage=storage, tz=tz)

    if ('На текущую неделю' == data or 'На следующую неделю' == data) and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule or schedule['schedule'] == []:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно\nПопробуйте позже⏱')
            statistics.add(action=data, storage=storage, tz=tz)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_str, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        bot.send_message(chat_id=chat_id, text=f'Расписание {group}\n'
                                               f'Неделя: {week_name}',
                         reply_markup=keyboards.make_keyboard_start_menu())
        # Отправка расписания
        schedule_processing.sending_schedule(bot=bot, chat_id=chat_id, schedule_str=schedule_str)

        statistics.add(action=data, storage=storage, tz=tz)



    elif 'Расписание на сегодня 🍏' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно🚫😣\n'
                                                   'Попробуйте позже⏱',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Расписание на сегодня', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()
        # Если курс нуль, тогда это преподаватель
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            schedule_one_day = get_one_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            schedule_one_day = get_one_day_schedule_in_str_prep(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_one_day, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        if not schedule_one_day:
            bot.send_message(chat_id=chat_id, text='Сегодня пар нет 😎')
            return
        bot.send_message(chat_id=chat_id, text=f'{schedule_one_day}')
        statistics.add(action='Расписание на сегодня', storage=storage, tz=tz)




    elif 'Экзамены' in data and user.get('group'):
        # Если курс нуль, тогда это преподаватель

        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = groups_exam(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = groups_exam(group=group)

        print(group)
        print(schedule)

        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание экзаменов временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Экзамены', storage=storage, tz=tz)
            return

        # schedule = schedule['schedule']

        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            schedule_exams = schedule_view_exams(schedule=schedule)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            schedule_exams = schedule_view_exams(schedule=schedule)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_exams, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)

            return

        schedule_processing.sending_schedule(bot=bot, chat_id=chat_id, schedule_str=schedule_exams)

        statistics.add(action='Экзамены', storage=storage, tz=tz)




    elif 'Расписание на завтра 🍎' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно🚫😣\n'
                                                   'Попробуйте позже⏱',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Расписание на завтра', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()
        if datetime.today().isoweekday() == 7:
            if week == 'odd':
                week = 'even'
            elif week == 'even':
                week = 'odd'
            else:
                week = 'all'

        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            schedule_next_day = get_next_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            schedule_next_day = get_next_day_schedule_in_str_prep(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_next_day, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        if not schedule_next_day:
            bot.send_message(chat_id=chat_id, text='Завтра пар нет 😎')
            return
        bot.send_message(chat_id=chat_id, text=f'{schedule_next_day}')
        statistics.add(action='Расписание на завтра', storage=storage, tz=tz)

    elif 'Ближайшая пара ⏱' in data and user.get('group'):
        bot.send_message(chat_id=chat_id, text='Ближайшая пара',
                         reply_markup=keyboards.make_keyboard_nearlesson())
        statistics.add(action='Ближайшая пара', storage=storage, tz=tz)
        return


    elif 'Текущая' in data and user.get('group'):
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно🚫😣\n'
                                                   'Попробуйте позже⏱',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Текущая', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()

        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(now_lessons, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        # если пар нет
        if not now_lessons:
            bot.send_message(chat_id=chat_id, text='Сейчас пары нет, можете отдохнуть)',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Текущая', storage=storage, tz=tz)
            return

        # Студент
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            now_lessons_str = get_now_lesson_in_str_stud(now_lessons)

        # Преподаватель
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            now_lessons_str = get_now_lesson_in_str_prep(now_lessons)

        # Проверяем, что расписание сформировалось
        if isinstance(now_lessons_str, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        bot.send_message(chat_id=chat_id, text=f'🧠Текущая пара🧠\n'f'{now_lessons_str}',
                         reply_markup=keyboards.make_keyboard_start_menu())

        statistics.add(action='Текущая', storage=storage, tz=tz)

    elif 'Следующая' in data and user.get('group'):
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно🚫😣\n'
                                                   'Попробуйте позже⏱',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()

        near_lessons = get_near_lesson(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(near_lessons, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        # если пар нет
        if not near_lessons:
            bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=tz)
            return

        # Студент
        if storage.get_user(chat_id=chat_id)['course'] != 'None':
            near_lessons_str = get_now_lesson_in_str_stud(near_lessons)

        # Преподаватель
        elif storage.get_user(chat_id=chat_id)['course'] == 'None':
            near_lessons_str = get_now_lesson_in_str_prep(near_lessons)

        # Проверяем, что расписание сформировалось
        if isinstance(near_lessons_str, APIError):
            schedule_processing.sending_schedule_is_not_available(bot=bot, chat_id=chat_id)
            return

        bot.send_message(chat_id=chat_id, text=f'🧠Ближайшая пара🧠\n'f'{near_lessons_str}',
                         reply_markup=keyboards.make_keyboard_start_menu())

        statistics.add(action='Следующая', storage=storage, tz=tz)
