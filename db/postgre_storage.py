import os
from datetime import datetime, date

import pendulum
import psycopg2
from psycopg2.extras import DictCursor

import dotenv
from sqlalchemy import create_engine, func, cast, Numeric
from sqlalchemy.orm import Session

from db.models.postgres_models import Vacpara, RealGroup, Prepod, Auditorie, DisciplineDB, \
    ScheduleMetaprogramDiscipline, ScheduleV2, QueryDB
from db.models.response_models import LessonsTime, Institute, Group, Teacher, Classroom, Discipline, OtherDiscipline, \
    Schedule, Query

from tools.schedule_tools.utils import get_now

dotenv.load_dotenv()

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

POSTGRES_DATABASE = f"postgresql+psycopg2://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_DATABASE}"

engine = create_engine(POSTGRES_DATABASE, echo=True)


class PostgresStorageCursor(object):
    def __enter__(self):
        self.connection = psycopg2.connect(**db_params)
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)

        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
        self.connection.close()


def get_start_date_of_study_year(study_date: date) -> datetime:
    september_first = datetime(study_date.year, 9, 1)

    if study_date.month >= 9 or study_date.isocalendar()[1] == september_first.isocalendar()[1]:
        september_first = datetime(study_date.year, 9, 1)
    else:
        september_first = datetime(study_date.year - 1, 9, 1)

    return datetime.fromisoformat(pendulum.instance(september_first).start_of("week").to_datetime_string())


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
    with Session(engine) as session:
        institutes = session.query(RealGroup) \
            .distinct(RealGroup.faculty_title) \
            .where(RealGroup.faculty_title != '') \
            .order_by(RealGroup.faculty_title) \
            .all()

        return [Institute(i).dict() for i in institutes]


def get_courses_by_institute(institute_id: int) -> list:
    with Session(engine) as session:
        courses = session.query(RealGroup) \
            .distinct(RealGroup.kurs) \
            .where((RealGroup.faculty_id == institute_id) & (RealGroup.is_active == True)) \
            .order_by(RealGroup.kurs) \
            .all()

        return [c.kurs for c in courses]


# def get_groups_by_institute_and_course(institute_id: int, course: int) -> list:
#     query = """
#         SELECT obozn AS name,
#                id_7  AS group_id
#         FROM real_groups
#         WHERE faculty_id = {institute}
#           AND kurs = {course}
#           AND is_active = True
#         ORDER BY name;
#     """.format(institute=institute_id, course=course)
#
#     with PostgresStorageCursor() as cursor:
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         groups = [dict(group) for group in rows]
#         return groups


def get_groups_by_institute_and_course(institute_id: int, course: int) -> list:
    with Session(engine) as session:
        groups = session.query(RealGroup) \
            .where((RealGroup.faculty_id == institute_id) & (RealGroup.kurs == course) & (RealGroup.is_active == True)) \
            .order_by(RealGroup.obozn) \
            .all()

        return [Group(g).dict() for g in groups]


def get_groups(is_active=True) -> list:
    with Session(engine) as session:
        groups = session.query(RealGroup) \
            .where((RealGroup.is_active == True) if (is_active) else True) \
            .order_by(RealGroup.obozn) \
            .all()

        return [Group(g).dict() for g in groups]


def get_teachers() -> list:
    with Session(engine) as session:
        teachers = session.query(Prepod) \
            .where(Prepod.preps != '') \
            .order_by(Prepod.preps) \
            .all()

        return [Teacher(t).dict() for t in teachers]


def get_classrooms() -> list:
    with Session(engine) as session:
        classrooms = session.query(Auditorie) \
            .where((Auditorie.obozn != '') & (Auditorie.obozn != '-')) \
            .order_by(Auditorie.obozn) \
            .all()

        return [Classroom(c).dict() for c in classrooms]


def get_schedule_by_group(group_id: int) -> list:
    start_of_first_week = pendulum.instance(get_now()).start_of("week")
    start_of_second_week = pendulum.instance(start_of_first_week).add(weeks=1).date()
    start_of_first_week = start_of_first_week.date()

    start_date_of_study_year = get_start_date_of_study_year(get_now())

    with Session(engine) as session:
        difference_of_weeks = cast(
            func.trunc(
                func.date_part(
                    'day',
                    ScheduleV2.dbeg - start_date_of_study_year
                ) / 7
            ), Numeric)

        schedule = session.query(ScheduleV2, Vacpara, RealGroup, Prepod) \
            .join(Vacpara, ScheduleV2.para == Vacpara.id_66) \
            .join(RealGroup, RealGroup.id_7 == func.any(ScheduleV2.groups)) \
            .join(Prepod, Prepod.id_61 == func.any(ScheduleV2.teachers), isouter=True) \
            .where(RealGroup.id_7 == group_id) \
            .where((start_of_first_week <= ScheduleV2.dbeg) & (ScheduleV2.dbeg <= start_of_second_week)) \
            .where((ScheduleV2.everyweek == 2) |
                   ((ScheduleV2.everyweek == 1) & (ScheduleV2.day > 7) & (difference_of_weeks % 2 == 1)) |
                   ((ScheduleV2.everyweek == 1) & (ScheduleV2.day <= 7) & (difference_of_weeks % 2 == 0))) \
            .order_by(ScheduleV2.dbeg) \
            .all()

        return [Schedule(s, vacpara) for s, vacpara, prepods, teachers in schedule]

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

    with PostgresStorageCursor() as cursor:
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

    with PostgresStorageCursor() as cursor:
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

    with PostgresStorageCursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        schedules = [dict(schedule) for schedule in rows]

        return schedules
