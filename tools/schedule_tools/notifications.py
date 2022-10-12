from datetime import timedelta

from tools.messages import reminder_messages


def get_reminders_status(time: int) -> str:
    if not time or time == 0:
        notifications_status = reminder_messages['status_disabled']
    else:
        notifications_status = reminder_messages['status_enabled'].format(time=time)
    return notifications_status


def calculating_reminder_times(schedule, time: int) -> dict:
    even = {}
    odd = {}

    for day in schedule:
        even[day['day']] = []
        odd[day['day']] = []
        for lesson in day['lessons']:
            if lesson['name'] == 'свободно':
                continue
            lesson_time = lesson['time'].split(':')
            hours = int(lesson_time[0])
            minutes = int(lesson_time[-1])

            if lesson['week'] == 'even' or lesson['week'] == 'all':
                even[day['day']].append(
                    str((timedelta(hours=hours, minutes=minutes) - timedelta(minutes=time)))[:-3]
                )

            if lesson['week'] == 'odd' or lesson['week'] == 'all':
                odd[day['day']].append(
                    str((timedelta(hours=hours, minutes=minutes) - timedelta(minutes=time)))[:-3]
                )

    reminders = {
        'even': even,
        'odd': odd
    }

    return reminders
