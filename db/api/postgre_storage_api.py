import os
import calendar
from datetime import datetime, date

import dotenv
import pendulum as pendulum

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models.postgres_models import LessonsTimeDB, GroupDB, TeacherDB, ClassroomDB, DisciplinesDB, OtherDisciplineDB, \
    ScheduleDB
from db.models.response_models import LessonsTime, Institute, Group, Teacher, Classroom, Disciplines, OtherDiscipline, \
    Schedule

dotenv.load_dotenv()

PG_DB_DATABASE = os.environ.get('PG_DB_DATABASE', default='schedule')
PG_DB_USER = os.environ.get('PG_DB_USER')
PG_DB_PASSWORD = os.environ.get('PG_DB_PASSWORD')
PG_DB_HOST = os.environ.get('PG_DB_HOST')
PG_DB_PORT = os.environ.get('PG_DB_PORT', default='5432')

POSTGRES_DATABASE = f"postgresql+psycopg2://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_DATABASE}"

engine = create_engine(POSTGRES_DATABASE, echo=True)


def is_even_week(start_date: date):
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

    return weeks % 2 == 1


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
        classrooms = session.query(ClassroomDB).where(ClassroomDB.obozn != '' and ClassroomDB.obozn != '-') \
            .order_by(ClassroomDB.id_60).all()

        return list(map(lambda x: Classroom(id_60=x.id_60, obozn=x.obozn), classrooms))


def get_disciplines() -> list:
    with Session(engine) as session:
        disciplines = session.query(DisciplinesDB).where(DisciplinesDB.title != '').order_by(DisciplinesDB.id).all()

        return list(map(lambda x: Disciplines(id=x.id, title=x.title, real_title=x.real_title), disciplines))


def get_other_disciplines() -> list:
    with Session(engine) as session:
        other_disciplines = session.query(OtherDisciplineDB) \
            .where(OtherDisciplineDB.is_active == True and OtherDisciplineDB.project_active == True) \
            .order_by(OtherDisciplineDB.id).all()

        return list(map(lambda x: OtherDiscipline(
            id=x.id, discipline_title=x.discipline_title, type=x.type, is_online=x.is_online), other_disciplines))


def get_schedule(start_date: datetime) -> list:
    start_of_first_week = pendulum.instance(start_date).start_of("week")
    start_of_second_week = pendulum.instance(start_of_first_week).add(weeks=1)

    with Session(engine) as session:
        schedules = session.query(ScheduleDB) \
            .where(start_of_first_week.date() <= ScheduleDB.dbeg) \
            .where(ScheduleDB.dbeg <= start_of_second_week.date()) \
            .order_by(ScheduleDB.id).all()

        schedules = list(filter(lambda s: (s.everyweek == 2 or s.everyweek == 1 and s.day > 7) if is_even_week(s.dbeg)
                else (s.everyweek == 2 or s.everyweek == 1 and s.day <= 7), schedules))

        return list(map(lambda x: Schedule(
            id=x.id,
            groups=x.groups,
            groups_verbose=x.groups_verbose,
            teachers=x.teachers,
            teachers_verbose=x.teachers_verbose,
            auditories=x.auditories,
            auditories_verbose=x.auditories_verbose,
            discipline=x.discipline,
            discipline_verbose=x.discipline_verbose,
            meta_program_discipline_id=x.meta_program_discipline_id,
            para=x.para,
            type=x.type,
            ngroup=x.ngroup,
            nt=x.nt,
            dbeg=x.dbeg,
            day=x.day,
            everyweek=x.everyweek
        ), schedules))


def get_schedule_month(year: int, month: int) -> list:
    start_day_of_month = date(year, month, 1)
    end_day_of_month = date(year, month, calendar.monthrange(year, month)[1])

    with Session(engine) as session:
        schedules = session.query(ScheduleDB) \
            .where(start_day_of_month <= ScheduleDB.dbeg) \
            .where(ScheduleDB.dbeg <= end_day_of_month) \
            .order_by(ScheduleDB.id).all()

        schedules = list(filter(lambda s: (s.everyweek == 2 or s.everyweek == 1 and s.day > 7) if is_even_week(s.dbeg)
                else (s.everyweek == 2 or s.everyweek == 1 and s.day <= 7), schedules))

        return list(map(lambda x: Schedule(
            id=x.id,
            groups=x.groups,
            groups_verbose=x.groups_verbose,
            teachers=x.teachers,
            teachers_verbose=x.teachers_verbose,
            auditories=x.auditories,
            auditories_verbose=x.auditories_verbose,
            discipline=x.discipline,
            discipline_verbose=x.discipline_verbose,
            meta_program_discipline_id=x.meta_program_discipline_id,
            para=x.para,
            type=x.type,
            ngroup=x.ngroup,
            nt=x.nt,
            dbeg=x.dbeg,
            day=x.day,
            everyweek=x.everyweek
        ), schedules))
