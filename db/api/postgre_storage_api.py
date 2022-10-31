import os
from contextlib import closing
from datetime import datetime, date, timedelta

import dotenv
import pytz
import pendulum as pendulum
import psycopg2
from psycopg2.extras import DictCursor

TIME_ZONE = pytz.timezone('Asia/Irkutsk')

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


def get_lessons() -> list:
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT "
                           "id_66 as id_lesson, "
                           "para as lesson_number, "
                           "begtime, "
                           "endtime "
                           "from vacpara")
            rows = cursor.fetchall()
            lessons = [dict(lesson) for lesson in rows]
            return lessons


def get_institutes() -> list:
    query = """
        SELECT DISTINCT faculty_id    AS institute_id,
                        faculty_title AS institute_title
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


def get_groups() -> list:
    query = """
        SELECT id_7       AS group_id,
               obozn      AS name,
               kurs       AS course,
               faculty_id AS institute_id
        FROM real_groups
        WHERE is_active IS TRUE
        ORDER BY name;
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
        ORDER BY fullname;
    """

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            teachers = [dict(teacher) for teacher in rows]
            return teachers


def get_classrooms() -> list:
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT "
                           "id_60 as id_auditories, "
                           "obozn as name "
                           "from auditories")
            rows = cursor.fetchall()
            auditories = [dict(auditory) for auditory in rows]
            return auditories


def get_disciplines() -> list:
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT "
                           "id as id_disciplines, "
                           "title as name "
                           "from disciplines")
            rows = cursor.fetchall()
            disciplines = [dict(discipline) for discipline in rows]
            return disciplines


def get_schedule(start_date: datetime = datetime.now(TIME_ZONE)) -> list:
    """Получение расписания групп из PostgreSQL"""

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
        SELECT
            id as id_schedule,
            groups as ids_groups,
            groups_verbose,
            teachers as ids_teachers,
            teachers_verbose,
            auditories as ids_auditories,
            auditories_verbose,
            discipline,
            discipline_verbose,
            para as id_lesson,
            dbeg as date_begin,
            day,
            ngroup as subgroup,
            nt as lesson_type
            from schedule_v2
        WHERE (
            (dbeg = '{odd_week:%Y-%m-%d}' and (everyweek = 2 or everyweek = 1 and day <= 7))
            or (dbeg = '{even_week:%Y-%m-%d}' and (everyweek = 2 or everyweek = 1 and day > 7))
            )
    """.format(odd_week=odd_week, even_week=even_week)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]
            return schedules


def get_schedule_year(year: int = datetime.now().year) -> list:
    """Получение расписания групп из PostgreSQL"""

    start_study_year = date(year, 9, 1)
    end_study_year = date(start_study_year.year + 1, 6, 30)

    query = """
        SELECT
            id as id_schedule,
            groups as ids_groups,
            groups_verbose,
            teachers as ids_teachers,
            teachers_verbose,
            auditories as ids_auditories,
            auditories_verbose,
            discipline,
            discipline_verbose,
            para as id_lesson,
            dbeg as date_begin,
            day,
            ngroup as subgroup,
            nt as lesson_type
            from schedule_v2
        WHERE dbeg between '{start_study_year}' and '{end_study_year}'
    """.format(start_study_year=start_study_year, end_study_year=end_study_year)

    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            schedules = [dict(schedule) for schedule in rows]
            return schedules
