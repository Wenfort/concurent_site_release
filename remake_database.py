import postgres_mode as pm
import requests
from bs4 import BeautifulSoup
import time

while True:
    domains = pm.custom_request_to_database_with_return("SELECT name FROM concurent_site.main_domain "
                                                        "WHERE age = 777 "
                                                        "LIMIT 10;")
    if not domains:
        break

    for domain_pack in domains:
        domain = domain_pack[0]
        URL = f'https://www.nic.ru/whois/?searchWord={domain}'
        r = requests.get(URL).content
        soup = BeautifulSoup(r, 'html.parser').text

        try:
            if 'Creation Date' in soup:
                start = soup.find('Creation Date') + 15
                finish = start + 4
                item = soup[start:finish]
                domain_age = 2021 - int(item)
            elif 'Registered on' in soup:
                start = soup.find('Registered on')
                finish = soup.find('Registry fee')
                item = soup[start:finish].split()[4]
                domain_age = 2021 - int(item)
            elif 'created' in soup:
                if '.lv' in domain or '.club' in domain or '.to' in domain or '.ua' in domain or '.eu' in domain:
                    domain_age = 5
                else:
                    start = soup.find('created') + 8
                    finish = start + 4
                    item = soup[start:finish]
                    domain_age = 2021 - int(item)
        except:
            print(f'Возраст домена {domain} определен неправильно')
            domain_age = 5

        print(f'Домен {domain} собран, возраст {domain_age}')
        pm.custom_request_to_database_without_return(f"UPDATE concurent_site.main_domain SET age = {domain_age} WHERE name = '{domain}';")
        time.sleep(1)