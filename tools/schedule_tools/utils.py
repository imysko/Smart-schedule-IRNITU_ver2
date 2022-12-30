from datetime import datetime, timedelta

import pytz

TIMEZONE = pytz.timezone('Asia/Irkutsk')


def get_now():
    return datetime.now(TIMEZONE) - timedelta(21)
