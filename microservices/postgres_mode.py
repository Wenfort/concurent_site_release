import psycopg2

DATABASE = 'postgres'
SCHEMA = 'concurent_site'
USER = 'postgres'
PASSWORD = 'fn3kMls1'
HOST = '127.0.0.1'

def establish_connection():
    connection = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    return connection

def check_in_database(table, row_check, value_check, limit=0):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()

    if not limit:
        limit = ''
    else:
        limit = f' LIMIT {str(limit)}'

    if type(value_check) is int:
        sql = f"SELECT * FROM {SCHEMA}.{table} WHERE {row_check}>='{value_check}'{limit}"
    else:
        sql = f"SELECT * FROM {SCHEMA}.{table} WHERE {row_check}='{value_check}'{limit}"
    cursor.execute(sql)
    check = cursor.fetchall()
    conn.close()
    return check


def get_data_from_database(table, limit=0):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    if limit == 0:
        sql = f'SELECT * FROM {SCHEMA}.{table}'
    else:
        sql = f'SELECT * FROM {SCHEMA}.{table} LIMIT {limit}'
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    return data


def add_to_database_with_autoincrement(table, values_to_go):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    sql = f"INSERT INTO {SCHEMA}.{table} VALUES (DEFAULT,{('%s,' * len(values_to_go))[0:-1]})"
    cursor.execute(sql, (values_to_go))
    conn.commit()
    conn.close()


def add_to_database(table, values_to_go):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    sql = f"INSERT INTO {SCHEMA}.{table} VALUES ({('%s,' * len(values_to_go))[0:-1]});"
    cursor.execute(sql, (values_to_go))
    conn.commit()
    conn.close()


def delete_from_database(table, row, values):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    for value in values:
        sql = f"DELETE FROM {SCHEMA}.{table} WHERE {row} = '{value}'"
        cursor.execute(sql)
    conn.commit()
    conn.close()


def update_database(table, row_update, value_update, where_row, value):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    sql = f"UPDATE {SCHEMA}.{table} SET {row_update} = '{value_update}' WHERE {where_row} = '{value}'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


def delete_from_database(table, row, values):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    for value in values:
        sql = f"DELETE FROM {SCHEMA}.{table} WHERE {row} = '{value}'"
        cursor.execute(sql)
    conn.commit()
    conn.close()

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