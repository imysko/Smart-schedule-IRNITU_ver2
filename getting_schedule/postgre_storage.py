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


def get_institutes() -> dict:
    with closing(psycopg2.connect(**db_params)) as conn:
        print('Database opened successfully')
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id_5, fac from vacfac")
            rows = cursor.fetchall()

            for row in rows:
                print(dict(row))

    print("\nOperation done successfully")


get_institutes()
