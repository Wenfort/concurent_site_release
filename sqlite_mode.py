import sqlite3


def add_to_database(database, table, values_to_go):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    sql = f"INSERT INTO {table} VALUES ({('?,' * len(values_to_go))[0:-1]})"
    cursor.executemany(sql, [values_to_go])
    conn.commit()
    conn.close()


def add_to_database_with_autoincrement(database, table, values_to_go):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    sql = f"INSERT INTO {table} VALUES ({('null,' + '?,' * len(values_to_go))[0:-1]})"
    cursor.executemany(sql, [values_to_go])
    conn.commit()
    conn.close()


def check_in_database(database, table, row_check, value_check, limit = 0):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    if not limit:
        limit = ''
    else:
        limit = f' LIMIT {str(limit)}'

    if type(value_check) is int:
        sql = f'SELECT * FROM {table} WHERE {row_check}>=?'
    else:
        sql = f'SELECT * FROM {table} WHERE {row_check}=?'
    cursor.execute(sql, [value_check])
    check = cursor.fetchall()
    conn.close()
    return check


def get_data_from_database(database, table, limit=0):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if limit == 0:
        sql = f'SELECT * FROM {table}'
    else:
        sql = f'SELECT * FROM {table} LIMIT {limit}'
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    return data


def update_database(database, table, row_update, value_update, where_row, value):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    sql = f'UPDATE {table} SET {row_update} = "{value_update}" WHERE {where_row} = "{value}"'
    cursor.execute(sql)
    conn.commit()
    conn.close()


def delete_from_database(database, table, row, values):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    for value in values:
        sql = f'DELETE FROM {table} WHERE {row} = "{value}"'
        cursor.execute(sql)
    conn.commit()
    conn.close()


def count_items_from_database(database, table):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    sql = f'SELECT COUNT (*) FROM {table}'
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return result
