import os
from contextlib import closing
from datetime import datetime, date

import pytz
from dotenv import load_dotenv
import pendulum
import psycopg2
from psycopg2.extras import DictCursor

from tools.schedule_tools.utils import get_now

load_dotenv()


PG_DB_DATABASE = os.environ.get('PG_DB_DATABASE', default='schedule')
PG_DB_USER = os.environ.get('PG_DB_USER')
PG_DB_PASSWORD = os.environ.get('PG_DB_PASSWORD', default='')
PG_DB_HOST = os.environ.get('PG_DB_HOST')
PG_DB_PORT = os.environ.get('PG_DB_PORT', default='5432')

db_params = {
    'database': PG_DB_DATABASE,
    'user': PG_DB_USER,
    'password': PG_DB_PASSWORD,
    'host': PG_DB_HOST,
    'port': PG_DB_PORT
}


def is_week_even(start_date: datetime) -> bool:
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


def get_odd_even_week():
    date_now = get_now()
    start_of_first_week = pendulum.instance(date_now).start_of("week")
    start_of_second_week = pendulum.instance(start_of_first_week).add(weeks=1)

    is_even = is_week_even(date_now)
    if is_even == 1:
        odd_week = start_of_second_week
        even_week = start_of_first_week
    else:
        even_week = start_of_second_week
        odd_week = start_of_first_week

    return odd_week, even_week


def get_institutes() -> list:
    query = """
        SELECT DISTINCT faculty_title AS institute_title,
                        faculty_id    AS institute_id
        FROM real_groups
        WHERE faculty_title NOT LIKE ''
        ORDER BY institute_title;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            institutes = [dict(institute) for institute in rows]
            return institutes


def get_courses_by_institute(institute_id: int) -> list:
    query = f"""
        SELECT DISTINCT kurs AS course
        FROM real_groups
        WHERE faculty_id = {institute_id}
          AND is_active = True
        ORDER BY course;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            courses = [course[0] for course in rows]
            return courses


def get_groups_by_institute_and_course(institute_id: int, course: int) -> list:
    query = """
        SELECT obozn AS name,
               id_7  AS group_id
        FROM real_groups
        WHERE faculty_id = {institute}
          AND kurs = {course}
          AND is_active = True
        ORDER BY name;
    """.format(institute=institute_id, course=course)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            groups = [dict(group) for group in rows]
            return groups


def get_groups(is_active=True) -> list:
    query = """
           SELECT obozn AS name,
                  id_7  AS group_id
           FROM real_groups
       """

    if is_active:
        query += "  WHERE is_active = True"

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            groups = [dict(group) for group in rows]
            return groups


def get_teachers() -> list:
    query = """
        SELECT preps AS fullname,
               id_61 AS teacher_id
        FROM prepods
        ORDER BY fullname;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            teachers = [dict(teacher) for teacher in rows]
            return teachers


def get_classrooms() -> list:
    query = """
        SELECT obozn AS name,
               id_60 AS classroom_id
        FROM auditories
        ORDER BY name;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            classrooms = [dict(classroom) for classroom in rows]
            return classrooms


def get_schedule_by_group(group_id: int) -> list:
    odd_week, even_week = get_odd_even_week()

    query = """
        SELECT vacpara.para                AS lesson_number,
               vacpara.begtime             AS lesson_start,
               vacpara.endtime             AS lesson_end,
               schedule.discipline_verbose AS name,
               groups.obozn                AS list_group,
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
        WHERE {group_id} = groups.id_7
          AND groups.is_active = TRUE
          AND ((schedule.dbeg = '{odd_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day <= 7))
            OR (schedule.dbeg = '{even_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day > 7)))
        ORDER BY dbeg, day, lesson_number, subgroup;
    """.format(odd_week=odd_week, even_week=even_week, group_id=group_id)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]

            return schedules


def get_schedule_by_teacher(teacher_id: int) -> list:
    odd_week, even_week = get_odd_even_week()

    query = """
        SELECT DISTINCT vacpara.para                AS lesson_number,
                        vacpara.begtime             AS lesson_start,
                        vacpara.endtime             AS lesson_end,
                        schedule.discipline_verbose AS name,
                        groups.obozn                AS list_group,
                        teachers.preps              AS teacher_fullname,
                        schedule.auditories_verbose AS classroom,
                        schedule.nt                 AS lesson_type,
                        schedule.ngroup             AS subgroup,
                        (schedule.day - 1) % 7 + 1  AS day,
                        schedule.dbeg
        FROM schedule_v2 AS schedule
                 JOIN vacpara
                      ON schedule.para = vacpara.id_66
                 JOIN prepods AS teachers
                      ON teachers.id_61 = ANY (schedule.teachers)
                 JOIN real_groups AS groups
                      ON groups.id_7 = ANY (schedule.groups)
        WHERE {teacher_id} = ANY (schedule.teachers)
          AND groups.is_active = TRUE
          AND ((schedule.dbeg = '{odd_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day <= 7))
            OR (schedule.dbeg = '{even_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day > 7)))
        ORDER BY dbeg, day, lesson_number, subgroup;
    """.format(odd_week=odd_week, even_week=even_week, teacher_id=teacher_id)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]

            return schedules


def get_schedule_by_classroom(classroom_id: int) -> list:
    odd_week, even_week = get_odd_even_week()

    query = """
        SELECT DISTINCT vacpara.para                AS lesson_number,
                        vacpara.begtime             AS lesson_start,
                        vacpara.endtime             AS lesson_end,
                        schedule.discipline_verbose AS name,
                        groups.obozn                AS list_group,
                        teachers.preps              AS teacher_fullname,
                        schedule.auditories_verbose AS classroom,
                        schedule.nt                 AS lesson_type,
                        schedule.ngroup             AS subgroup,
                        (schedule.day - 1) % 7 + 1  AS day,
                        schedule.dbeg
        FROM schedule_v2 AS schedule
                 JOIN vacpara
                      ON schedule.para = vacpara.id_66
                 JOIN prepods AS teachers
                      ON teachers.id_61 = ANY (schedule.teachers)
                 JOIN real_groups AS groups
                      ON groups.id_7 = ANY (schedule.groups)
                 JOIN auditories as classrooms
                      ON classrooms.obozn = schedule.auditories_verbose
        WHERE {classroom_id} = classrooms.id_60
          AND groups.is_active = TRUE
          AND ((schedule.dbeg = '{odd_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day <= 7))
            OR (schedule.dbeg = '{even_week:%Y-%m-%d}' AND (everyweek = 2 OR everyweek = 1 AND day > 7)))
        ORDER BY dbeg, day, lesson_number, subgroup;
    """.format(odd_week=odd_week, even_week=even_week, classroom_id=classroom_id)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]

            return schedules
