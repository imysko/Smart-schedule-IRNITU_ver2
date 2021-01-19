from datetime import datetime, date
import pytz

from functions import schedule_tools

TIME_ZONE = pytz.timezone('Asia/Irkutsk')

# Режим отладки (если включен, то не определяем текущее время - позволяет использовать старое расписание).
DEBUG = False

DAYS = schedule_tools.DAYS


def convert_institutes(pg_institutes: list) -> list:
    """Преобразование формата институтов"""
    if not pg_institutes:
        raise ValueError('Данные не могут быть пустыми')
    result_data = [{'name': institute['fac']} for institute in pg_institutes]
    return result_data


def convert_groups(pg_groups: list) -> list:
    """Преобразование формата групп"""
    if not pg_groups:
        raise ValueError('Данные не могут быть пустыми')
    result_data = [{
        'name': group['obozn'],
        'course': f"{group['kurs']} курс",
        'institute': group['fac']
    } for group in pg_groups]

    return result_data


def convert_courses(mongo_groups: list) -> list:
    """Получение курсов из информации о группах"""
    if not mongo_groups:
        raise ValueError('Данные не могут быть пустыми')

    # Удаляем информацию о курсе, меняем ключ course на name
    for group in mongo_groups:
        group.pop('name', None)
        group.pop('_id', None)
        group['name'] = group.pop('course')

    # Удаляем поторяющиеся элементы
    courses = []
    for item in mongo_groups:
        if item not in courses:
            courses.append(item)
    return courses


def convert_teachers(pg_teachers: list) -> list:
    mongo_teachers = pg_teachers
    for teacher in mongo_teachers:
        teacher['prep'] = teacher['prep'].strip()
        teacher['prep_short_name'] = teacher['prep_short_name'].strip()

        # Удаляем пустого преподавателя
        if not teacher['prep'] and not teacher['prep_short_name']:
            mongo_teachers.remove(teacher)

    return mongo_teachers


def convert_schedule(pg_schedule: list) -> list:
    """Преобразование формата расписания"""

    date_now = datetime.now(TIME_ZONE).date()

    if DEBUG:
        date_now = date(2020, 12, 20)  # ДЛЯ ОТЛАДКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Сортируем массив, чтобы одинаковые группы стояли рядом.
    pg_schedule = sorted(pg_schedule, key=lambda x: x['obozn'])

    all_schedule = []

    schedule = []  # Расписание группы.

    item_index = 0  # Счетчик индекса.
    for item in pg_schedule:

        # Проверяем, что расписание действует
        if date_now <= item['dend']:

            week, day = schedule_tools.getting_week_and_day_of_week(item)

            # Определяем вид пары и подгруппу.
            info = schedule_tools.forming_info_data(nt=item['nt'], ngroup=item["ngroup"])

            lesson = {
                'time': item['begtime'],
                'week': week,
                'name': item['title'],
                'aud': item['auditories_verbose'],
                'info': info,
                'prep': item['preps'].strip().strip('.'),
            }

            # Смотрим, создал ли уже нужный день в расписании.
            if not schedule_tools.is_there_dict_with_value_in_list(schedule, day):
                schedule.append(
                    {
                        'day': day,
                        'lessons': []
                    }
                )

            # Добавляем пары в нужный день.
            for sch in schedule:
                if sch['day'] == day:
                    if lesson in sch['lessons']:
                        break
                    sch['lessons'].append(lesson)
                    break

        # Если нашлась другая группа или это последний элемент списка, сохраняем предыдущую.
        current_group = item['obozn']
        next_group = ''
        if item_index != len(pg_schedule) - 1:
            next_group = pg_schedule[item_index + 1]['obozn']

        if current_group != next_group or item_index == len(pg_schedule) - 1:
            # Проверяем, что расписание не пустое
            if schedule:
                # Сортируем пары в дне по времени и подгруппе
                schedule_tools.sorting_lessons_in_a_day_by_time_and_ngroup(schedule=schedule)

                all_schedule.append({
                    'group': current_group,
                    'schedule': schedule_tools.days_in_right_order(schedule)
                })

                # Обнуляем расписание для слудующей группы
                schedule = []

        item_index += 1  # Увеличиваем счетчик индекса.
    return all_schedule


def convert_teachers_schedule(pg_schedule: list) -> list:
    """Преобразование формата расписания преподавателей"""

    date_now = datetime.now(TIME_ZONE).date()
    if DEBUG:
        date_now = date(2020, 12, 20)  # ДЛЯ ОТЛАДКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Сортируем массив, чтобы одинаковые преподаватели стояли рядом.
    pg_schedule = sorted(pg_schedule, key=lambda x: x['prep_id'])

    all_schedule = []

    schedule = []  # Расписание преподавателя.

    item_index = 0  # Счетчик индекса.
    for item in pg_schedule:

        # Проверяем, что расписание действует
        if date_now <= item['dend']:

            week, day = schedule_tools.getting_week_and_day_of_week(item)

            # Определяем вид пары и подгруппу.
            info = schedule_tools.forming_info_data(nt=item['nt'], ngroup=item["ngroup"])

            lesson = {
                'time': item['begtime'],
                'week': week,
                'name': item['title'],
                'aud': item['auditories_verbose'],
                'info': info,
                'groups': [item['obozn']],  ## НУЖНО ДОБАВТЬ НЕСКОЛЬКО ГРУПП
            }

            # Смотрим, создал ли уже нужный день в расписании.
            if not schedule_tools.is_there_dict_with_value_in_list(schedule, day):
                schedule.append(
                    {
                        'day': day,
                        'lessons': []
                    }
                )

            # Добавляем пары в нужный день.
            for sch in schedule:
                if sch['day'] == day:
                    if lesson in sch['lessons']:
                        break

                    # Проверяем есть ли уже занятие в расписании
                    for day_lesson in sch['lessons']:
                        # Если есть, добавляем только группу
                        if lesson['time'] == day_lesson['time'] \
                                and lesson['week'] == day_lesson['week'] \
                                and lesson['name'] == day_lesson['name'] \
                                and lesson['aud'] == day_lesson['aud'] \
                                and lesson['info'] == day_lesson['info']:
                            day_lesson['groups'].append(item['obozn'])
                            break
                    else:  # Если нет, добавляем полностью пару.
                        sch['lessons'].append(lesson)
                    break

        # Если нашелся другой преподаватель или это последний элемент списка, сохраняем.
        current_prep_id = item['prep_id']
        next_prep_id = ''
        if item_index != len(pg_schedule) - 1:
            next_prep_id = pg_schedule[item_index + 1]['prep_id']

        if current_prep_id != next_prep_id or item_index == len(pg_schedule) - 1:
            # Проверяем, что расписание не пустое
            if schedule:
                schedule_tools.sorting_lessons_in_a_day_by_time_and_ngroup(schedule=schedule)

                all_schedule.append({
                    'prep': item['preps'].strip(),
                    'prep_short_name': item['prep_short_name'].strip(),
                    'pg_id': current_prep_id,
                    'schedule': schedule_tools.days_in_right_order(schedule)
                })

                # Обнуляем расписание для слудующего преподавателя
                schedule = []

        item_index += 1  # Увеличиваем счетчик индекса.
    return all_schedule
