import os
from contextlib import closing
from datetime import datetime, date, timedelta

import pytz
import pendulum as pendulum
import psycopg2
from psycopg2.extras import DictCursor

import itertools

TIME_ZONE = pytz.timezone('Asia/Irkutsk')

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


def get_week_even(start_date: datetime):
    """
    Возвращает 0 если неделя нечетная, и 1 если неделя четная
    """
    september_1st = datetime(start_date.year, 9, 1)

    if start_date.month >= 9 or start_date.isocalendar()[1] == september_1st.isocalendar()[1]:
        september_1st = datetime(start_date.year, 9, 1)
    else:
        september_1st = datetime(start_date.year - 1, 9, 1)

    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, datetime.min.time())
    start_date = pendulum.instance(start_date)
    study_year_start = pendulum.instance(september_1st).start_of("week")
    weeks = (start_date - study_year_start).days // 7

    return weeks % 2


def get_institutes() -> list:
    query = """
        SELECT DISTINCT faculty_title AS institute_title
        FROM real_groups
        WHERE faculty_title NOT LIKE ''
        ORDER BY institute_title;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            institutes = [institute[0] for institute in rows]
            return institutes


def get_courses_by_institute(institute: str) -> list:
    query = """
        SELECT DISTINCT kurs AS course
        FROM real_groups
        WHERE faculty_title = '{institute}'
          AND is_active = True
    """.format(institute=institute)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            courses = [course[0] for course in rows]
            return courses


def get_groups_by_institute_and_course(institute: str, course: int) -> list:
    query = """
        SELECT obozn AS name
        FROM real_groups
        WHERE faculty_title = '{institute}'
          AND kurs = {course}
    """.format(institute=institute, course=course)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            groups = [group[0] for group in rows]
            return groups


def get_teachers() -> list:
    query = """
        SELECT preps AS fullname
        FROM prepods
        ORDER BY fullname;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            teachers = [teacher[0] for teacher in rows]
            return teachers


def get_schedule_by_group(group: str) -> list:
    date_now = datetime.now(TIME_ZONE)
    start_of_first_week = pendulum.instance(date_now).start_of("week")
    start_of_second_week = pendulum.instance(start_of_first_week).add(weeks=1)

    is_even = get_week_even(date_now)
    if is_even == 1:
        odd_week = start_of_second_week
        even_week = start_of_first_week
    else:
        even_week = start_of_second_week
        odd_week = start_of_first_week

    query = """
        SELECT vacpara.para                AS lesson_number,
               vacpara.begtime             AS lesson_start,
               vacpara.endtime             AS lesson_end,
               schedule.discipline_verbose AS name,
               teachers.preps              AS teacher_fullname,
               schedule.auditories_verbose AS classroom,
               schedule.nt                 AS lesson_type,
               schedule.ngroup             AS subgroup,
               (schedule.day - 1) % 7 + 1  AS day,
               schedule.dbeg
        FROM schedule_v2 AS schedule
                 JOIN vacpara
                      ON schedule.para = vacpara.id_66
                 LEFT JOIN prepods AS teachers
                           ON teachers.id_61 = ANY (schedule.teachers)
                 JOIN real_groups AS groups
                      ON groups.id_7 = ANY (schedule.groups)
        WHERE 'ИСТб-20-3' = groups.obozn
          AND groups.is_active = TRUE
          AND ((schedule.dbeg = '{odd_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day <= 7))
            OR (schedule.dbeg = '{even_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day > 7)))
        ORDER BY dbeg, day, lesson_number, subgroup;
    """.format(odd_week=odd_week, even_week=even_week, group=group)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]

            return schedules
