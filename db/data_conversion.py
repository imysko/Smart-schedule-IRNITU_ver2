from datetime import timedelta, datetime

DAY_OF_WEEK = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    7: 'Воскресенье'
}


def schedule_group_by_date(pg_schedule: list) -> list:
    if not pg_schedule:
        raise ValueError('Данные не могут быть пустыми')

    schedule_list = []

    for record in pg_schedule:
        date = (record['dbeg'] + timedelta(days=(record['day'] - 1)))
        day = DAY_OF_WEEK[record['day']]

        del record['dbeg']
        del record['day']

        if not any(item['date'] == date for item in schedule_list):
            schedule_list.append({
                'date': date,
                'day_of_week': day,
                'lessons': [record]
            })
        else:
            next(item for item in schedule_list if item['date'] == date)['lessons'].append(record)

    return schedule_list


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
    schedule_list = schedule_group_by_date(pg_schedule)

    if selected_date is not None:
        schedule_list = list(filter(lambda x: x['date'] == selected_date.date(), schedule_list))

    return schedule_list
