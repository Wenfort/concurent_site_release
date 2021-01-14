import requests
import sqlite_mode as sm
import time

def get_token():
    accounts_with_balance = sm.check_in_database('db.sqlite3', 'main_payload', 'balance', 25)
    token = accounts_with_balance[0][0]
    return token

def run():
    #TODO мб брать инфу еще и с линкпад
    domains = sm.check_in_database('db.sqlite3', 'main_domain', 'status', 'pending')
    total = 0
    if domains:
        token = get_token()
        for domain_data in domains:
            domain = domain_data[0]
            age = domain_data[1]
            request_json = requests.get(
                f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={token}&host={domain}&parameterList=mjDin,mjHin').json()

            if not request_json['success']:
                pass
            else:
                total += 1
                unique_backlinks = int(request_json["summary"]["mjDin"])
                total_backlinks = int(request_json["summary"]["mjHin"])
                sm.delete_from_database('db.sqlite3', 'main_domain', 'name', (domain,))
                sm.add_to_database('db.sqlite3', 'main_domain', (domain, age, unique_backlinks, total_backlinks, 'complete'))

    print(f'Добавлено {total} ссылок для доменов в БД. В очереди {len(domains)}.')

while True:
    run()
    time.sleep(30)