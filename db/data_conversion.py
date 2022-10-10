from datetime import timedelta, datetime


def convert_institutes(pg_institutes: list) -> list:
    if not pg_institutes:
        raise ValueError('Данные не могут быть пустыми')

    list_institutes = pg_institutes
    for institute in list_institutes:
        institute[institute['institute_title']] = '{"institute": "' + str(institute['institute_id']) + '"}'
        del institute['institute_title']
        del institute['institute_id']

    return list_institutes


def convert_groups(pg_groups: list) -> list:
    if not pg_groups:
        raise ValueError('Данные не могут быть пустыми')

    list_groups = pg_groups
    for group in list_groups:
        group[group['name']] = '{"group": "' + str(group['group_id']) + '"}'
        del group['name']
        del group['group_id']

    return list_groups


def convert_schedule(pg_schedule: list,
                     next_week: bool = False,
                     selected_date: datetime = None) -> list:

    if not pg_schedule:
        raise ValueError('Данные не могут быть пустыми')

    if not next_week:
        start_of_week = pg_schedule[0]['dbeg']
    else:
        start_of_week = pg_schedule[-1]['dbeg']

    pg_schedule = list(filter(lambda x: x['dbeg'] == start_of_week, pg_schedule))

    for record in pg_schedule:
        record['date'] = (record['dbeg'] + timedelta(days=(record['day'] - 1)))
        del record['dbeg']
        del record['day']

    if selected_date is not None:
        pg_schedule = list(filter(lambda x: x['date'] == selected_date.date(), pg_schedule))

    return pg_schedule
