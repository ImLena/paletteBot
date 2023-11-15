from psycopg2 import pool

host = "localhost"
dbname = "palette-bot"
user = "postgres"
password = "postgres"
port = "5432"

db_pool = pool.SimpleConnectionPool(
    1,
    10,
    host=host,
    dbname=dbname,
    user=user,
    password=password,
    port=port)


def get_connection():
    return db_pool.getconn()


def release_connection(conn):
    db_pool.putconn(conn)
