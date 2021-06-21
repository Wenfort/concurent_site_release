import psycopg2
import os

SCHEMA = 'concurent_site'

def establish_connection(type):
    if type == 'local':
        DATABASE = os.environ['LOCAL_DB_NAME']
        USER = os.environ['LOCAL_DB_NAME']
        PASSWORD = os.environ['LOCAL_DB_PASSWORD']
        HOST = os.environ['LOCAL_DB_HOST']
    else:
        DATABASE = os.environ['EXTERNAL_DB_NAME']
        USER = os.environ['EXTERNAL_DB_USER']
        PASSWORD = os.environ['EXTERNAL_DB_PASSWORD']
        HOST = os.environ['EXTERNAL_DB_HOST']

    connection = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST, port='5432')
    return connection


def clean_all_data_from_database(connection):
    cursor = connection.cursor()
    test_domains = ('test-domain-one.ru', 'test-domain-two.ru', 'test-domain-three.ru')
    sql = (f'DELETE FROM {SCHEMA}.main_order;'
           f'DELETE FROM {SCHEMA}.main_handledxml;'
           f'DELETE FROM {SCHEMA}.main_requestqueue;'
           f'DELETE FROM {SCHEMA}.main_request;'
           f'DELETE FROM {SCHEMA}.main_domain WHERE name IN {test_domains};')

    cursor.execute(sql)
    connection.commit()

def fetch_regions_from_production_to_testing(remote_connection, local_connection):
    remote_cursor = remote_connection.cursor()
    local_cursor = local_connection.cursor()

    sql = "SELECT * FROM concurent_site.main_region;"
    remote_cursor.execute(sql)
    data_set = remote_cursor.fetchall()

    for data in data_set:
        sql = f"INSERT INTO concurent_site.main_region VALUES {data};"
        local_cursor.execute(sql)

    local_connection.commit()

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


if __name__ == '__main__':
    pass
    #local_connection = establish_connection('local')
    #remote_connection = establish_connection('remote')

    #clean_all_data_from_database(local_connection)
    #order, orderstatus, handledxml, requestqueue, request, domain = get_data_from_database(remote_connection)
    #insert_data_to_database(local_connection)

    #fetch_regions_from_production_to_testing(remote_connection, local_connection)
    #local_connection.close()
    #remote_connection.close()
