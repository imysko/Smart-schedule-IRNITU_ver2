import sqlite3

from db.postgre_storage import PostgresStorageCursor


def divide_chunks(l, n):
    # looping till length l
    length = len(l)
    for i in range(0, len(l), n):
        yield l[i:i + n], i, length

def sqlite_generate_tables(sqlite_connection):
    c = sqlite_connection.cursor()
    c.execute(
        """
create table schedule_items (
id         integer not null
    constraint schedule_items_id_pk
        primary key autoincrement,
groups text,
group_id text,
ngroup     integer,
teacher_id integer,
auditory_id   integer,
discipline text,
type         integer,
para       integer,
day        integer,
everyweek  integer,
dbeg       date
);
""")
    c.execute("""
create table main.groups_lists
(
id               integer not null
    constraint groups_lists_id_pk
        primary key autoincrement,
schedule_item_id integer not null,
group_id         integer not null
);
""")
    c.execute("""
create table main.teachers
(
id        integer not null
    constraint teachers_id_pk
        primary key autoincrement,
name      integer,
full_name integer
);""")

    c.execute("""
-- auto-generated definition
create table groups (
id        integer not null
    constraint teachers_id_pk
        primary key autoincrement,
title      text,
kurs      integer,
faculty_id      integer
);
""")

    c.execute("""
-- auto-generated definition
create table auditories (
id        integer not null
    constraint teachers_id_pk
        primary key autoincrement,
title      integer,
capacity      integer,
type      integer
);
        """)

    c.execute("""

    -- auto-generated definition
create table faculties (
id        integer not null
    constraint faculties_id_pk
        primary key autoincrement,
title      integer
);
            """)

    c.close()


def sqlite_fill_groups(sqlite_connection):
    with PostgresStorageCursor() as pg_cursor:
        sqlite_cursor = sqlite_connection.cursor()

        query = """
        SELECT id_7 as id, obozn, kurs, faculty_id
        FROM real_groups
        WHERE is_active = True
        """
        pg_cursor.execute(query)
        records = []
        for item in pg_cursor:
            records.append((
                item['id'],
                item['obozn'],
                item['kurs'],
                item['faculty_id'],
            ))

        sqlite_cursor.executemany("""
        INSERT INTO groups VALUES(?,?,?,?);
        """, records)
        sqlite_connection.commit()

        query = """
        SELECT DISTINCT faculty_id, faculty_title
        FROM real_groups
        WHERE is_active = True
        """
        pg_cursor.execute(query)
        records = []
        for item in pg_cursor:
            records.append((
                item['faculty_id'],
                item['faculty_title'],
            ))

        sqlite_cursor.executemany("""
        INSERT INTO faculties VALUES(?,?);
        """, records)
        sqlite_connection.commit()


def sqlite_fill_teachers(sqlite_connection):
    with PostgresStorageCursor() as pg_cursor:
        sqlite_cursor = sqlite_connection.cursor()

        query = """
        SELECT id_61 as id, prep, preps
        FROM prepods
        """
        pg_cursor.execute(query)
        records = []
        for item in pg_cursor:
            records.append((
                item['id'],
                item['prep'],
                item['preps'],
            ))

        sqlite_cursor.executemany("""
        INSERT INTO teachers VALUES(?,?,?);
        """, records)
        sqlite_connection.commit()


def sqlite_fill_auditories(sqlite_connection):
    with PostgresStorageCursor() as pg_cursor:
        sqlite_cursor = sqlite_connection.cursor()

        query = """
        SELECT id_60 as id, obozn, korp, maxstud
        FROM auditories
        """
        pg_cursor.execute(query)
        records = []
        for item in pg_cursor:
            records.append((
                item['id'],
                item['obozn'],
                item['maxstud'],
                {19: 1, 20: 2}.get(item['korp'], 0),
            ))

        sqlite_cursor.executemany("""
        INSERT INTO auditories VALUES(?,?,?,?);
        """, records)
        sqlite_connection.commit()

def sqlite_fill_schedule_items(sqlite_connection):
    query = """
    SELECT id, groups,
          groups_verbose,
          teachers,
          teachers_verbose,
          auditories,
          auditories_verbose,
          discipline_verbose,
          para,
          day,
          everyweek,
          nt,
          dbeg,
          ngroup
      FROM schedule_v2
      WHERE type = 'day' and groups && (SELECT array_agg(id_7) FROM real_groups WHERE is_active = True)
      ORDER BY dbeg
    """

    with PostgresStorageCursor() as pg_cursor:
        sqlite_cursor = sqlite_connection.cursor()

        pg_cursor.execute(query)
        records = []
        for item in pg_cursor:
            records.append((
                item['id'],
                item['groups_verbose'],
                item['groups'][0] if len(item['groups']) == 1 else None,
                item['ngroup'],
                item['teachers'][0] if item['teachers'] else None,
                item['auditories'][0] if item['auditories'] else None,
                item['discipline_verbose'],
                item['nt'],
                item['para'],
                item['day'],
                item['everyweek'],
                item['dbeg'],
            ))

            if item['groups']:
                sqlite_cursor.executemany(f"""
                INSERT INTO groups_lists(schedule_item_id, group_id) VALUES(?, ?)
                """, [(item['id'], g) for g in item['groups']])

        for items, i, length in divide_chunks(records, 1000):
            sqlite_cursor.executemany("""
            INSERT INTO schedule_items VALUES(?,?,?,?,?,?,?,?,?,?,?,?);
            """, items)
            sqlite_connection.commit()
            print(f"{i} / {length}")

        sqlite_cursor.close()


def sqlite_generate():
    sqlite_connection = sqlite3.connect('result2.db')

    sqlite_generate_tables(sqlite_connection)
    sqlite_fill_groups(sqlite_connection)
    sqlite_fill_teachers(sqlite_connection)
    sqlite_fill_auditories(sqlite_connection)
    sqlite_fill_schedule_items(sqlite_connection)

    sqlite_connection.close()


if __name__ == '__main__':
    sqlite_generate()

