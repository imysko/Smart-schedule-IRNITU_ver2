from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Boolean, String, Date, ARRAY


class Base(DeclarativeBase, object):
    pass


class Vacpara(Base):
    __tablename__ = 'vacpara'

    id_66 = Column(Integer, primary_key=True)
    para = Column(String)
    begtime = Column(String)
    endtime = Column(String)


class RealGroup(Base):
    __tablename__ = 'real_groups'

    id_7 = Column(Integer, primary_key=True)
    obozn = Column(String)
    kurs = Column(Integer)
    is_active = Column(Boolean)
    faculty_id = Column(Integer)
    faculty_title = Column(String)


class Prepod(Base):
    __tablename__ = 'prepods'

    id_61 = Column(Integer, primary_key=True)
    preps = Column(String)
    prep = Column(String)


class Auditorie(Base):
    __tablename__ = 'auditories'

    id_60 = Column(Integer, primary_key=True)
    obozn = Column(String)


class DisciplineDB(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    real_title = Column(String)


class ScheduleMetaprogramDiscipline(Base):
    __tablename__ = 'schedule_metaprogramdiscipline'

    id = Column(Integer, primary_key=True)
    discipline_title = Column(String)
    is_online = Column(Boolean)
    type = Column(Integer)
    is_active = Column(Boolean)
    project_active = Column(Boolean)


class QueryDB(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True)
    description = Column(String)


class ScheduleV2(Base):
    __tablename__ = 'schedule_v2'

    id = Column(Integer, primary_key=True)
    groups = Column(ARRAY(Integer))
    groups_verbose = Column(String)
    teachers = Column(ARRAY(Integer))
    teachers_verbose = Column(String)
    auditories = Column(ARRAY(Integer))
    auditories_verbose = Column(String)
    discipline = Column(Integer)
    discipline_verbose = Column(String)
    meta_program_discipline_id = Column(Integer)
    query_id = Column(Integer)
    para = Column(Integer)
    type = Column(String)
    nt = Column(Integer)
    ngroup = Column(Integer)
    dbeg = Column(Date)
    day = Column(Integer)
    everyweek = Column(Integer)
