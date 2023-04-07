def convert_lessons_dict(pg_lessons: list):
    if not pg_lessons:
        raise ValueError('Данные не могут быть пустыми')

    return {'lessons': [lesson.__dict__() for lesson in pg_lessons]}


def convert_institutes_dict(pg_institutes: list):
    if not pg_institutes:
        raise ValueError('Данные не могут быть пустыми')

    return {'institutes': [institute.__dict__() for institute in pg_institutes]}


def convert_groups_dict(pg_groups: list):
    if not pg_groups:
        raise ValueError('Данные не могут быть пустыми')

    return {'groups': [group.__dict__() for group in pg_groups]}


def convert_teachers_dict(pg_teachers: list):
    if not pg_teachers:
        raise ValueError('Данные не могут быть пустыми')

    return {'teachers': [teacher.__dict__() for teacher in pg_teachers]}


def convert_classrooms_dict(pg_classrooms: list):
    if not pg_classrooms:
        raise ValueError('Данные не могут быть пустыми')

    return {'classrooms': [classroom.__dict__() for classroom in pg_classrooms]}


def convert_disciplines_dict(pg_disciplines: list):
    if not pg_disciplines:
        raise ValueError('Данные не могут быть пустыми')

    return {'disciplines': [discipline.__dict__() for discipline in pg_disciplines]}


def convert_other_disciplines_dict(pg_other_disciplines: list):
    if not pg_other_disciplines:
        raise ValueError('Данные не могут быть пустыми')

    return {'other_disciplines': [other_discipline.__dict__() for other_discipline in pg_other_disciplines]}


def convert_schedule_dict(pg_schedule: list):
    if not pg_schedule:
        raise ValueError('Данные не могут быть пустыми')

    return {'schedule': [schedule.__dict__() for schedule in pg_schedule]}

