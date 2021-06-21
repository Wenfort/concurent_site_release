import psycopg2
import os

DATABASE = os.environ['EXTERNAL_DB_NAME']
SCHEMA = 'concurent_site'
USER = os.environ['EXTERNAL_DB_USER']
PASSWORD = os.environ['EXTERNAL_DB_PASSWORD']
HOST = os.environ['EXTERNAL_DB_HOST']


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
