from datetime import timedelta
import pytz

TIME_ZONE = pytz.timezone('Asia/Irkutsk')


def convert_lessons_dict(pg_lessons: list):
    if not pg_lessons:
        raise ValueError('Данные не могут быть пустыми')

    list_lessons = sorted(pg_lessons, key=lambda value: value['lesson_number'])

    return {'lessons': list_lessons}


def convert_institutes_dict(pg_institutes: list):
    if not pg_institutes:
        raise ValueError('Данные не могут быть пустыми')

    list_institutes = sorted(pg_institutes, key=lambda value: value['name'])

    return {'institutes': list_institutes}


def convert_groups_dict(pg_groups: list):
    if not pg_groups:
        raise ValueError('Данные не могут быть пустыми')

    list_groups = sorted(pg_groups, key=lambda value: value['name'])

    return {'groups': list_groups}


def convert_teachers_dict(pg_teachers: list):
    if not pg_teachers:
        raise ValueError('Данные не могут быть пустыми')

    list_teachers = sorted(pg_teachers, key=lambda value: value['full_name'])

    return {'teachers': list_teachers}


def convert_auditories_dict(pg_auditories: list):
    if not pg_auditories:
        raise ValueError('Данные не могут быть пустыми')

    list_auditories = sorted(pg_auditories, key=lambda value: value['name'])

    return {'auditories': list_auditories}


def convert_disciplines_dict(pg_disciplines: list):
    if not pg_disciplines:
        raise ValueError('Данные не могут быть пустыми')

    list_disciplines = sorted(pg_disciplines, key=lambda value: value['name'])

    return {'disciplines': list_disciplines}


def convert_schedule_dict(pg_schedule: list):
    if not pg_schedule:
        raise ValueError('Данные не могут быть пустыми')

    for record in pg_schedule:
        record['date'] = (record['date_begin'] + timedelta(days=(record['day'] - 1) % 7)).__str__()
        del record['date_begin']
        del record['day']

    list_schedule = sorted(pg_schedule, key=lambda value: value['date'])

    return {'schedule': list_schedule}

