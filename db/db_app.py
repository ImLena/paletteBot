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


def setup_table():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS usersInfo (
                                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                                chat_id VARCHAR  UNIQUE,
                                clusters INTEGER);
                        """)
            connection.commit()
    except Exception as e:
        print("Произошла ошибка: ", e)
    finally:
        release_connection(connection)
    connection.commit()
