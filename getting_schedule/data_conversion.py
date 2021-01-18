from datetime import datetime, date
import pytz

TIME_ZONE = pytz.timezone('Asia/Irkutsk')


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


DAYS = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среда',
    4: 'четверг',
    5: 'пятница',
    6: 'суббота',
    7: 'воскресенье'
}


def getting_week_and_day_of_week(pg_lesson: dict) -> tuple:
    """Определение четности недели и дня недели"""

    if pg_lesson['everyweek'] == 2:
        week = 'all'
        day = DAYS[pg_lesson['day']]
    else:
        if pg_lesson['day'] <= 7:
            week = 'even'
            day = DAYS[pg_lesson['day']]
        else:
            week = 'odd'
            day = DAYS[pg_lesson['day'] - 7]

    return week, day


def is_there_dict_with_value_in_list(input_list_with_dict: list, value: str) -> bool:
    if not input_list_with_dict:
        return False

    for dict_item in input_list_with_dict:
        if value in dict_item.values():
            return True
    return False


def get_dict_key(d, value):
    """Получение ключа по значеню словаря"""
    for k, v in d.items():
        if v == value:
            return k


def convert_schedule(pg_schedule: list) -> list:
    """Преобразование формата расписания"""

    date_now = datetime.now(TIME_ZONE).date()

    # date_now = date(2020, 12, 20)  # ДЛЯ ОТЛАДКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Сортируем массив, чтобы одинаковые группы стояли рядом.
    pg_schedule = sorted(pg_schedule, key=lambda x: x['obozn'])

    all_schedule = []

    schedule = []  # Расписание группы.

    item_index = 0  # Счетчик индекса.
    for item in pg_schedule:

        # Проверяем, что расписание действует
        if date_now <= item['dend']:

            week, day = getting_week_and_day_of_week(item)

            # Определяем вид пары и подгруппу.
            if item['nt'] == 1:
                info = '( Лекция )'
            elif item['nt'] == 2:
                if item['ngroup']:
                    info = f'( Практ. подгруппа {item["ngroup"]} )'
                else:
                    info = '( Практ. )'
            else:
                if item['ngroup']:
                    info = f'( Лаб. раб. подгруппа {item["ngroup"]} )'
                else:
                    info = f'( Лаб. раб. )'

            lesson = {
                'time': item['begtime'],
                'week': week,
                'name': item['title'],
                'aud': item['auditories_verbose'],
                'info': info,
                'prep': item['preps'].strip(),
            }

            # Смотрим, создал ли уже нужный день в расписании.
            if not is_there_dict_with_value_in_list(schedule, day):
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
                for sch in schedule:
                    # Сортируем подгруппы
                    sch['lessons'] = sorted(sch['lessons'], key=lambda x: x['info'])
                    # Сортируем по времени
                    sch['lessons'] = sorted(sch['lessons'], key=lambda x: int(x['time'].replace(':', '')))

                all_schedule.append({
                    'group': current_group,
                    'schedule': sorted(schedule, key=lambda x: get_dict_key(DAYS, x['day']))
                })

                # Обнуляем расписание для слудующей группы
                schedule = []

        item_index += 1  # Увеличиваем счетчик индекса.
    return all_schedule


def convert_teachers_schedule(pg_schedule: list) -> list:
    """Преобразование формата расписания преподавателей"""

    date_now = datetime.now(TIME_ZONE).date()

    #date_now = date(2020, 12, 20)  # ДЛЯ ОТЛАДКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Сортируем массив, чтобы одинаковые преподаватели стояли рядом.
    pg_schedule = sorted(pg_schedule, key=lambda x: x['prep_id'])

    all_schedule = []

    schedule = []  # Расписание преподавателя.

    item_index = 0  # Счетчик индекса.
    for item in pg_schedule:

        # Проверяем, что расписание действует
        if date_now <= item['dend']:

            week, day = getting_week_and_day_of_week(item)

            # Определяем вид пары и подгруппу.
            if item['nt'] == 1:
                info = '( Лекция )'
            elif item['nt'] == 2:
                if item['ngroup']:
                    info = f'( Практ. подгруппа {item["ngroup"]} )'
                else:
                    info = '( Практ. )'
            else:
                if item['ngroup']:
                    info = f'( Лаб. раб. подгруппа {item["ngroup"]} )'
                else:
                    info = f'( Лаб. раб. )'

            lesson = {
                'time': item['begtime'],
                'week': week,
                'name': item['title'],
                'aud': item['auditories_verbose'],
                'info': info,
                'groups': [item['obozn']],  ## НУЖНО ДОБАВТЬ НЕСКОЛЬКО ГРУПП
            }

            # Смотрим, создал ли уже нужный день в расписании.
            if not is_there_dict_with_value_in_list(schedule, day):
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

        # Если нашелся другой преподаватель или это последний элемент списка, сохраняем.
        current_prep_id = item['prep_id']
        next_prep_id = ''
        if item_index != len(pg_schedule) - 1:
            next_prep_id = pg_schedule[item_index + 1]['prep_id']

        if current_prep_id != next_prep_id or item_index == len(pg_schedule) - 1:
            # Проверяем, что расписание не пустое
            if schedule:
                # Сортируем пары в дне по времени и подгруппе
                for sch in schedule:
                    # Сортируем подгруппы
                    sch['lessons'] = sorted(sch['lessons'], key=lambda x: x['info'])
                    # Сортируем по времени
                    sch['lessons'] = sorted(sch['lessons'], key=lambda x: int(x['time'].replace(':', '')))

                all_schedule.append({
                    'prep': item['preps'].strip(),
                    'prep_short_name': item['prep_short_name'].strip(),
                    'pg_id': current_prep_id,
                    'schedule': sorted(schedule, key=lambda x: get_dict_key(DAYS, x['day']))
                })

                # Обнуляем расписание для слудующего преподавателя
                schedule = []

        item_index += 1  # Увеличиваем счетчик индекса.
    return all_schedule
