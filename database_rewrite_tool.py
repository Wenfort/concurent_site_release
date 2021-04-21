import psycopg2

SCHEMA = 'concurent_site'


def establish_connection(type):
    if type == 'local':
        DATABASE = 'postgres'
        USER = 'postgres'
        PASSWORD = 'fn3kMls1'
        HOST = '127.0.0.1'
    else:
        DATABASE = 'project_live'
        USER = 'postgres'
        PASSWORD = 'fn3kMls1'
        HOST = '178.250.158.252'

    connection = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST, port='5432')
    return connection


def clean_all_data_from_database(connection):
    cursor = connection.cursor()
    sql = (f'DELETE FROM {SCHEMA}.main_order;'
           f'DELETE FROM {SCHEMA}.main_orderstatus;'
           f'DELETE FROM {SCHEMA}.main_handledxml;'
           f'DELETE FROM {SCHEMA}.main_requestqueue;'
           f'DELETE FROM {SCHEMA}.main_request;'
           f'DELETE FROM {SCHEMA}.main_domain;')

    cursor.execute(sql)
    connection.commit()


def get_data_from_database(connection):
    def get_data_from_table(table):
        sql = f"SELECT * FROM {SCHEMA}.{table};"
        cursor.execute(sql)
        data = cursor.fetchall()

        return data

    cursor = connection.cursor()

    order = get_data_from_table('main_order')
    orderstatus = get_data_from_table('main_orderstatus')
    handledxml = get_data_from_table('main_handledxml')
    requestqueue = get_data_from_table('main_requestqueue')
    request = get_data_from_table('main_request')
    domain = get_data_from_table('main_domain')

    return order, orderstatus, handledxml, requestqueue, request, domain


def insert_data_to_database(connection):
    def insert_data_to_table(dataset, table):
        for data in dataset:
            sql = f"INSERT INTO {SCHEMA}.{table} VALUES {data};"
            cursor.execute(sql)

    cursor = connection.cursor()

    insert_data_to_table(orderstatus, 'main_orderstatus')
    insert_data_to_table(request, 'main_request')
    insert_data_to_table(requestqueue, 'main_requestqueue')
    insert_data_to_table(handledxml, 'main_handledxml')
    insert_data_to_table(order, 'main_order')
    insert_data_to_table(domain, 'main_domain')
    connection.commit()


local_connection = establish_connection('local')
remote_connection = establish_connection('remote')

clean_all_data_from_database(local_connection)
order, orderstatus, handledxml, requestqueue, request, domain = get_data_from_database(remote_connection)
insert_data_to_database(local_connection)
