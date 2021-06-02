import psycopg2

DATABASE = 'postgres'
SCHEMA = 'concurent_site'
USER = 'postgres'
PASSWORD = 'fn3kMls1'
HOST = '127.0.0.1'


def custom_request_to_database_without_return(sql):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def custom_request_to_database_with_return(sql, fetchone=''):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    cursor.execute(sql)
    if fetchone:
        data = cursor.fetchone()
    else:
        data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data
