import os
from contextlib import closing

import psycopg2
from psycopg2.extras import DictCursor

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
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT fac from vacfac")
            rows = cursor.fetchall()
            institutes = [dict(institute) for institute in rows]
            return institutes


def get_groups() -> list:
    """Получение групп из PostgreSQL"""
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Вместо id института подставляется сразу название.
            cursor.execute("SELECT groups.obozn, groups.kurs, vacfac.fac "
                           "from groups join vacfac "
                           "on groups.fac = vacfac.id_5")
            rows = cursor.fetchall()
            groups = [dict(group) for group in rows]
            return groups


def get_teachers() -> list:
    """Получение преподавателей из PostgreSQL"""
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Вместо id института подставляется сразу название.
            cursor.execute("SELECT "
                           "preps as prep, "
                           "prep as prep_short_name, "
                           "id_61 as prep_id "
                           "from prepods")
            rows = cursor.fetchall()
            teachers = [dict(teacher) for teacher in rows]
            return teachers


def get_schedule() -> list:
    """Получение расписания групп из PostgreSQL"""
    with closing(psycopg2.connect(**db_params)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
SELECT coalesce(g.obozn, '') as obozn, dbeg, dend, begtime, everyweek, preps, prep_short_name, prep_id, auditories_verbose, day, nt, title, ngroup
FROM (
           SELECT unnest(groups)   group_id,
                  dbeg,
                  dend,
                  vacpara.begtime,
                  everyweek,
                  prepods.preps,
                  prepods.prep  as prep_short_name,
                  prepods.id_61 as prep_id,
                  CASE
                      when -1 = any (s.auditories) then 'онлайн'
                      else auditories.obozn
                      end
                                as auditories_verbose,
                  day,
                  nt,
                  coalesce(disciplines.title, discipline_verbose) as title,
                  ngroup
           from schedule_v2 s
                    join vacpara on s.para = vacpara.id_66
                    left join prepods on prepods.id_61 = any (s.teachers)
                    left join disciplines on s.discipline = disciplines.id
                    left join auditories on auditories.id_60 = any (s.auditories)
) t
LEFT JOIN groups g ON t.group_id = g.id_7
""")

            rows = cursor.fetchall()
            groups = [dict(group) for group in rows]
            return groups
