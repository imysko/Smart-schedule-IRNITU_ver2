from datetime import datetime, timedelta

import pytz

TIMEZONE = pytz.timezone('Asia/Irkutsk')


def get_now():
    return datetime.now(TIMEZONE)


def divide_chunks(l, n):
    # looping till length l
    length = len(l)
    for i in range(0, len(l), n):
        yield l[i:i + n], i, length