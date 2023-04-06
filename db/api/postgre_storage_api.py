import os
import calendar
from contextlib import closing
from datetime import datetime, date

import dotenv
import pendulum as pendulum
import psycopg2
from psycopg2.extras import DictCursor

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models.database_models import LessonsTimeDB, GroupDB, TeacherDB, ClassroomDB, DisciplinesDB
from db.models.response_models import LessonsTime, Institute, Group, Teacher, Classroom, Disciplines

dotenv.load_dotenv()

PG_DB_DATABASE = os.environ.get('PG_DB_DATABASE', default='schedule')
PG_DB_USER = os.environ.get('PG_DB_USER')
PG_DB_PASSWORD = os.environ.get('PG_DB_PASSWORD')
PG_DB_HOST = os.environ.get('PG_DB_HOST')
PG_DB_PORT = os.environ.get('PG_DB_PORT', default='5432')

engine = create_engine(
    f"postgresql+psycopg2://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_DATABASE}"
)

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


def get_lessons_time() -> list:
    with Session(engine) as session:
        lessons_time = session.query(LessonsTimeDB).order_by(LessonsTimeDB.id_66).all()

        return list(map(lambda x: LessonsTime(
            id_66=x.id_66, para=x.para, begtime=x.begtime, endtime=x.endtime), lessons_time))


def get_institutes() -> list:
    with Session(engine) as session:
        institutes = session.query(GroupDB).distinct(GroupDB.faculty_title).where(GroupDB.faculty_title != '').all()

        return sorted(list(map(lambda x: Institute(
            faculty_id=x.faculty_id, faculty_title=x.faculty_title), institutes)), key=lambda i: i.institute_id)


def get_groups() -> list:
    with Session(engine) as session:
        groups = session.query(GroupDB).where(GroupDB.is_active == True).order_by(GroupDB.id_7).all()

        return list(map(lambda x: Group(id_7=x.id_7, obozn=x.obozn, kurs=x.kurs, faculty_id=x.faculty_id), groups))


def get_teachers() -> list:
    with Session(engine) as session:
        teacher = session.query(TeacherDB).where(TeacherDB.preps != '').order_by(TeacherDB.id_61).all()

        return list(map(lambda x: Teacher(id_61=x.id_61, preps=x.preps, prep=x.prep), teacher))


def get_classrooms() -> list:
    with Session(engine) as session:
        classrooms = session.query(ClassroomDB).where(ClassroomDB.obozn != '' and ClassroomDB.obozn != '-')\
            .order_by(ClassroomDB.id_60).all()

        return list(map(lambda x: Classroom(id_60=x.id_60, obozn=x.obozn), classrooms))


def get_disciplines() -> list:
    with Session(engine) as session:
        disciplines = session.query(DisciplinesDB).where(DisciplinesDB.title != '').order_by(DisciplinesDB.id).all()

        return list(map(lambda x: Disciplines(id=x.id, title=x.title, real_title=x.real_title), disciplines))


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
