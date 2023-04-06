from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Boolean, String


class Base(DeclarativeBase, object):
    pass


class LessonsTimeDB(Base):
    __tablename__ = 'vacpara'

    id_66 = Column(Integer, primary_key=True)
    para = Column(String)
    begtime = Column(String)
    endtime = Column(String)


class GroupDB(Base):
    __tablename__ = 'real_groups'

    id_7 = Column(Integer, primary_key=True)
    obozn = Column(String)
    kurs = Column(Integer)
    is_active = Column(Boolean)
    faculty_id = Column(Integer)
    faculty_title = Column(String)


class TeacherDB(Base):
    __tablename__ = 'prepods'

    id_61 = Column(Integer, primary_key=True)
    preps = Column(String)
    prep = Column(String)


class ClassroomDB(Base):
    __tablename__ = 'auditories'

    id_60 = Column(Integer, primary_key=True)
    obozn = Column(String)


class DisciplinesDB(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    real_title = Column(String)
