import os
import calendar
from contextlib import closing
from datetime import datetime, date

import dotenv
import pytz
import pendulum as pendulum
import psycopg2
from psycopg2.extras import DictCursor

dotenv.load_dotenv()

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


def get_lessons() -> list:
    query = """
        SELECT id_66 AS lesson_id,
               para  AS lesson_number,
               begtime,
               endtime
        FROM vacpara
        ORDER BY lesson_number
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            lessons = [dict(lesson) for lesson in rows]
            return lessons


def get_institutes() -> list:
    query = """
        SELECT DISTINCT faculty_id    AS institute_id,
                        faculty_title AS institute_title
        FROM real_groups
        WHERE faculty_title NOT LIKE ''
        ORDER BY institute_title
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            institutes = [dict(institute) for institute in rows]
            return institutes


def get_groups() -> list:
    query = """
        SELECT id_7       AS group_id,
               obozn      AS name,
               kurs       AS course,
               faculty_id AS institute_id
        FROM real_groups
        WHERE is_active IS TRUE
        ORDER BY name
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            groups = [dict(group) for group in rows]
            return groups


def get_teachers() -> list:
    query = """
        SELECT id_61  AS teacher_id,
               preps  AS fullname,
               prep   AS shortname
        FROM prepods
        WHERE NOT preps = ''
        ORDER BY fullname
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            teachers = [dict(teacher) for teacher in rows]
            return teachers


def get_classrooms() -> list:
    query = """
        SELECT id_60 AS classroom_id,
               obozn AS name
        FROM auditories
        WHERE NOT obozn = '-'
          AND NOT obozn = ''
        ORDER BY name
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            classrooms = [dict(classroom) for classroom in rows]
            return classrooms


def get_disciplines() -> list:
    query = """
        SELECT id AS discipline_id,
               title,
               real_title
        FROM disciplines
        WHERE NOT title = ''
        ORDER BY title
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            disciplines = [dict(discipline) for discipline in rows]
            return disciplines


def get_schedule(start_date: datetime) -> list:
    start_of_first_week = pendulum.instance(start_date).start_of("week")
    start_of_second_week = pendulum.instance(start_of_first_week).add(weeks=1)

    is_even = get_week_even(start_date)
    if is_even == 1:
        odd_week = start_of_second_week
        even_week = start_of_first_week
    else:
        even_week = start_of_second_week
        odd_week = start_of_first_week

    query = """
        SELECT id                            AS schedule_id,
               groups                        AS groups_ids,
               groups_verbose,
               teachers                      AS teachers_ids,
               teachers_verbose,
               auditories                    AS auditories_ids,
               auditories_verbose,
               discipline                    AS discipline_id,
               discipline_verbose,
               para                          AS lesson_id,
               dbeg,
               (schedule_v2.day - 1) % 7 + 1 AS day,
               ngroup                        AS subgroup,
               nt                            AS lesson_type
        FROM schedule_v2
        WHERE ((dbeg = '{odd_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day <= 7))
            OR (dbeg = '{even_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day > 7)))
        ORDER BY dbeg, day, lesson_id, subgroup
    """.format(odd_week=odd_week, even_week=even_week)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]
            return schedules


def get_schedule_month(year: int, month: int) -> list:
    start_day_of_month = date(year, month, 1)
    end_day_of_month = date(year, month, calendar.monthrange(year, month)[1])

    query = """
        SELECT id                            AS schedule_id,
               groups                        AS groups_ids,
               groups_verbose,
               teachers                      AS teachers_ids,
               teachers_verbose,
               auditories                    AS auditories_ids,
               auditories_verbose,
               discipline                    AS discipline_id,
               discipline_verbose,
               para                          AS lesson_id,
               dbeg,
               (schedule_v2.day - 1) % 7 + 1 AS day,
               ngroup                        AS subgroup,
               nt                            AS lesson_type
        FROM schedule_v2
        WHERE dbeg BETWEEN '{start_day_of_month}' AND '{end_day_of_month}'
        ORDER BY dbeg, day, lesson_id, subgroup
    """.format(start_day_of_month=start_day_of_month, end_day_of_month=end_day_of_month)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]
            return schedules
