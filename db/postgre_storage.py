import os
import re
from contextlib import closing
from datetime import datetime

import pendulum as pendulum
import psycopg2
from psycopg2.extras import DictCursor

from data_conversion import TIME_ZONE, get_week_even

PG_DB_DATABASE = os.environ.get('PG_DB_DATABASE', default='schedule')
PG_DB_USER = os.environ.get('PG_DB_USER')
PG_DB_PASSWORD = os.environ.get('PG_DB_PASSWORD')
PG_DB_HOST = os.environ.get('PG_DB_HOST')
PG_DB_PORT = os.environ.get('PG_DB_PORT', default='5432')

db_params = {
    'database': PG_DB_DATABASE,
    'user': PG_DB_USER,
    'password': PG_DB_PASSWORD,
    'host': PG_DB_HOST,
    'port': PG_DB_PORT
}


def get_institutes() -> list:
    """Получение институтов из PostgreSQL"""
    return []


def get_groups() -> list:
    """Получение групп из PostgreSQL"""
    return []


def get_teachers() -> list:
    """Получение преподавателей из PostgreSQL"""
    return []


def get_schedule() -> list:
    """Получение расписания групп из PostgreSQL"""
    return []
