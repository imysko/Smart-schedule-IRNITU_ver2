from itertools import groupby


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
        group['name'] = group.pop('course')
    mongo_groups = sorted(mongo_groups, key=lambda x: x['name'])  # Сортируем массив

    # Удаляем поторяющиеся элементы
    courses = []
    for item in mongo_groups:
        if item not in courses:
            courses.append(item)
    return courses
