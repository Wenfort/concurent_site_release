import requests
import postgres_mode as pm
import time

def get_token():
    accounts_with_balance = pm.check_in_database('main_payload', 'balance', 25)
    token = accounts_with_balance[0][0]
    return token

def run():
    domains = pm.check_in_database('main_domain', 'status', 'pending')
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
                pm.delete_from_database('main_domain', 'name', (domain,))
                pm.add_to_database('main_domain', (domain, age, unique_backlinks, total_backlinks, 'complete'))

    print(f'Добавлено {total} ссылок для доменов в БД. В очереди {len(domains)}: {domains}.')

while True:
    run()
    time.sleep(30)