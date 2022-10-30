from datetime import timedelta, datetime

from tools.messages import reminder_messages

DEBUG = False


def get_reminders_status(time: int) -> str:
    if not time or time == 0:
        notifications_status = reminder_messages['status_disabled']
    else:
        notifications_status = reminder_messages['status_enabled'].format(time=time)
    return notifications_status


def calculating_reminder_times(schedule: list, time: int) -> dict:
    reminders = {}

    for day in schedule:
        reminders[day['day_of_week'].lower()] = []
        for lesson in day['lessons']:
            lesson_time = lesson['lesson_start'].split(':')
            hours = int(lesson_time[0])
            minutes = int(lesson_time[-1])

            reminders[day['day_of_week'].lower()].append(
                str((timedelta(hours=hours, minutes=minutes) - timedelta(minutes=time)))[:-3]
            )

    return reminders


def check_that_the_lesson_has_the_right_time(time, lesson_time) -> bool:
    if DEBUG:
        return True
    return time in lesson_time


def check_that_user_has_reminder_enabled_for_the_current_time(time_now, user_day_reminder_time: list) -> bool:
    if DEBUG:
        return True
    if user_day_reminder_time is None:
        return False
    user_day_reminder_time = [datetime.strptime(time, '%H:%M').strftime('%H:%M') for time in user_day_reminder_time]
    return time_now.strftime('%H:%M') in user_day_reminder_time


def forming_user_to_submit(
        chat_id: int,
        group: str,
        notifications: int,
        day_now: str,
        time_now: datetime
) -> dict:
    lesson_time = (time_now + timedelta(minutes=notifications)).strftime('%H:%M')

    user = {
        'chat_id': chat_id,
        'group': group,
        'day': day_now,
        'notifications': notifications,
        'time': lesson_time
    }

    return user


def convert_minutes_word(minutes: int):
    match minutes % 10:
        case 1 if minutes != 11:
            string = "минуту"
        case 2 if minutes != 12:
            string = "минуты"
        case 3 if minutes != 13:
            string = "минуты"
        case 4 if minutes != 14:
            string = "минуты"
        case _:
            string = "минут"

    return string
