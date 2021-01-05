from conc_settings import *
from multiprocessing import Process, Queue
from threading import Thread
from loguru import logger
import time
import pymorphy2
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from sqlite_mode import *


@logger.catch
class Manager:
    def __init__(self):
        self.requests = tuple()
        self.yandex_objects_list = list()
        self.process_list = ''
        self.q = Queue()

        self.get_requests_from_queue()
        self.make_processes()
        self.run_processes()
        self.get_data_from_processes()

        self.refresh_balance()
        self.delete_requests_from_queue()


        print('stop')

    def get_requests_from_queue(self):
        items = get_data_from_database('db.sqlite3', 'main_requestqueue')
        reqs = list()
        for item in items:
            reqs.append(item[0])

        self.requests = tuple(reqs)


    def make_processes(self):
        self.process_list = [Thread(target=Yandex, args=(request.lower(), self.q)) for request in self.requests]

    def run_processes(self):
        for process in self.process_list:
            process.start()

    def get_data_from_processes(self):
        for process in self.process_list:
            self.yandex_objects_list.append(self.q.get())

    def refresh_balance(self):
        keys_and_tokens = check_in_database('db.sqlite3', 'main_payload', 'balance', 35)
        for item in keys_and_tokens:
            key = item[0]
            r = requests.get(f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={key}&host=yandex.ru&parameterList=').json()
            balance = r['hostLimitsBalance']
            update_database('db.sqlite3', 'main_payload', 'balance', balance, 'key', key)

    def delete_requests_from_queue(self):
        delete_from_database('db.sqlite3', 'main_requestqueue', self.requests)


@logger.catch
class Site:
    def __init__(self, position, soup):

        self.soup = soup
        self.position = position
        self.url = ''
        self.domain = ''
        self.site_type = ''
        self.html = ''
        self.domain_object = ''
        self.content_object = ''

        self.get_url()
        self.get_domain()
        self.get_site_type()

        if self.site_type == 'organic':
            self.get_html()

        self.make_content_object()
        self.make_domain_object()

    def get_url(self):
        self.url = self.soup.find('a', 'organic__url').get('href')

    def get_site_type(self):
        if 'data-fast-wzrd' in self.soup:
            self.site_type = 'wizard'
        elif 'yandex.ru' in self.url or 'youtube.com' in self.url or 'wikipedia.org' in self.url:
            if 'yabs' in self.url:
                self.site_type = 'direct'
            else:
                self.site_type = 'super'
        else:
            self.site_type = 'organic'

    def get_domain(self):
        self.domain = urlparse(self.url)
        self.domain = self.domain.netloc
        self.domain.replace('www.', '')

        while self.domain.count('.') != 1:
            first_dot = self.domain.find('.') + 1
            self.domain = self.domain[first_dot:]

    def get_html(self):
        r = requests.get(self.url, headers=HEADERS, verify=False).content
        self.html = BeautifulSoup(r, 'html.parser')

    def make_domain_object(self):
        self.domain_object = Domain(self.domain)

    def make_content_object(self):
        self.content_object = Content(self.html, self.site_type, self.domain)


@logger.catch
class Yandex:
    def __init__(self, request, q):
        self.request = request
        self.q = q
        self.stemmed_request = list()
        self.page_url = ''
        self.page_html = ''
        self.site_list = ''
        self.site_objects_list = list()
        self.thread_list = ''
        self.concurency_object = ''
        self.result = dict()

        self.start_logging()

        if not self.check_request_in_db():
            self.stem_request()
            self.get_page_url()
            self.get_page_html()
            self.get_site_list()

            self.make_threads()
            self.run_threads()
            self.check_threads()

            self.make_concurency_object()
            self.add_result_to_database()
            self.check_request_in_db()

        self.q.put(self.result)

    def start_logging(self):
        logger.add("debug.txt", format="{time:HH:mm:ss} {message}", encoding="UTF-8")
        logger.debug('Класс Yandex создан')
        logger.info(f'Запрос: {self.request}')

    def check_request_in_db(self):
        check = check_in_database('db.sqlite3', 'main_request', 'request', self.request)
        if check[0][8] == 'ready':
            self.result = check
            return True

    def stem_request(self):
        morph = pymorphy2.MorphAnalyzer()
        self.stemmed_request = morph.parse(self.request)[0].normal_form.split()
        logger.info(f'Стемированный запрос: {self.stemmed_request}')

    def get_page_url(self):
        self.page_url = f'https://yandex.ru/search/?text={self.request}&lr={REGIONS["Москва"]}'

    def get_page_html(self):
        r = requests.get(self.page_url, headers=HEADERS).content
        self.page_html = BeautifulSoup(r, 'html.parser')

    def get_site_list(self):
        self.site_list = self.page_html.find_all('li', 'serp-item')
        logger.info(f'Собран список сайтов')

    def make_site_object(self, position, site):
        self.site_objects_list.append(Site(position, site))

    def make_threads(self):
        self.thread_list = [Thread(target=self.make_site_object, args=(str(position), site)) for position, site in
                            enumerate(self.site_list, 1)]

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def make_concurency_object(self):
        self.concurency_object = Concurency(self.site_objects_list, self.stemmed_request)

    def prepare_result(self):
        self.result = {
            'Запрос': self.request,
            'Конкуренция по возрасту': self.concurency_object.site_age_concurency,
            'Конкуренция по стему': self.concurency_object.site_stem_concurency,
            'Конкуренция по объему': self.concurency_object.site_volume_concurency,
            'Конкуренция по ссылочному': self.concurency_object.site_backlinks_concurency,
            'Итоговая конкуренция': self.concurency_object.site_total_concurency,
            'Модификатор директ': self.concurency_object.direct_upscale,
        }

    def add_result_to_database(self):

        delete_from_database('db.sqlite3', 'main_request', (self.request,))


        values_to_go = (self.request,
                        self.concurency_object.site_age_concurency,
                        self.concurency_object.site_stem_concurency,
                        self.concurency_object.site_volume_concurency,
                        self.concurency_object.site_backlinks_concurency,
                        self.concurency_object.site_total_concurency,
                        self.concurency_object.direct_upscale,
                        'ready')
        logger.debug(values_to_go)
        add_to_database_with_autoincrement('db.sqlite3', 'main_request', values_to_go)

    def get_scalp(self):
        print(self.page_html.prettify())


@logger.catch
class Backlinks:
    def __init__(self, domain):
        self.domain = domain
        self.token = ''
        self.request_json = ''
        self.total_backlinks = ''
        self.unique_backlinks = ''

        self.get_token()
        self.get_backlinks()

    def get_token(self):
        accounts_with_balance = check_in_database('db.sqlite3', 'main_payload', 'balance', 25)
        self.token = accounts_with_balance[0][0]

    def get_backlinks(self):

        self.request_json = requests.get(
            f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={self.token}&host={self.domain}&parameterList=mjDin,mjHin').json()

        if self.request_json['success'] == False:
            logger.info(f'{self.domain} данные не получены по причине {self.request_json["message"]}')
            self.unique_backlinks = 0
            self.total_backlinks = 0
        else:
            self.unique_backlinks = int(self.request_json["summary"]["mjDin"])
            self.total_backlinks = int(self.request_json["summary"]["mjHin"])
            # logger.info(f'Данные {self.domain} получены. Всего ссылок: {self.request_json["summary"]["mjHin"]}. Уникальных ссылок: {self.request_json["summary"]["mjDin"]}')


@logger.catch
class Domain:
    def __init__(self, domain):
        self.domain = domain
        self.domain_age = ''
        self.backlinks = ''
        self.backlinks_object = ''

        self.check_data_in_database()

    def check_data_in_database(self):
        check = check_in_database('db.sqlite3', 'main_domain', 'name', self.domain)

        if check:
            self.domain_age = check[0][1]
            self.backlinks = check[0][2]
        else:
            self.get_domain_age()
            self.make_backlinks_object()
            self.backlinks = self.backlinks_object.unique_backlinks
            values_to_go = (
                self.domain, self.domain_age, self.backlinks,
                self.backlinks_object.total_backlinks)
            add_to_database('db.sqlite3', 'main_domain', values_to_go)

        if self.backlinks == 0:
            self.make_backlinks_object()
            self.backlinks = self.backlinks_object.unique_backlinks
            update_database('db.sqlite3', 'main_domain', 'unique_backlinks', self.backlinks_object.unique_backlinks,
                            'name', self.domain)
            update_database('db.sqlite3', 'main_domain', 'total_backlinks', self.backlinks_object.total_backlinks,
                            'name', self.domain)

    def get_domain_age(self):
        URL = f'https://www.nic.ru/whois/?searchWord={self.domain}'
        r = requests.get(URL).content
        soup = BeautifulSoup(r, 'html.parser').text

        if 'Creation Date' in soup:
            start = soup.find('Creation Date') + 15
            finish = start + 4
            item = soup[start:finish]
            self.domain_age = 2020 - int(item)
        elif 'created' in soup:
            if 'com.ua' in self.domain:
                self.domain_age = 5
            elif '.ua' in self.domain:
                start = soup.find('Creation Date') + 18
                finish = start + 4
                item = soup[start:finish]
                self.domain_age = 2020 - int(item)
            elif '.lv' in self.domain or '.club' in self.domain:
                self.domain_age = 5
            else:
                start = soup.find('created') + 8
                finish = start + 4
                item = soup[start:finish]
                self.domain_age = 2020 - int(item)

        if self.domain_age > 10:
            self.domain_age = 10

    def make_backlinks_object(self):
        self.backlinks_object = Backlinks(self.domain)


@logger.catch
class Content:
    def __init__(self, html, site_type, domain):
        self.domain = domain
        self.html = html
        self.site_type = site_type
        self.text = ''
        self.letters_amount = ''
        self.words_amount = ''
        self.title = ''
        self.stemmed_title = list()

        if self.site_type == 'organic':
            logger.add("critical.txt", format="{time:HH:mm:ss} {message}", level='CRITICAL', encoding="UTF-8")
            try:
                self.get_text()
                self.count_letters_amount()
                self.get_title()
                self.stem_title()
            except:
                logger.critical(f"ЖОПА {self.domain}. ")
                self.letters_amount = 5000

    def get_text(self):
        self.text = self.html.text.replace('\n', '')

    def count_letters_amount(self):
        self.letters_amount = len(self.text)

        if self.letters_amount > 10000:
            self.letters_amount = 10000

    def count_words_amount(self):
        pass

    def get_title(self):
        self.title = self.html.find('title').text
        self.title = self.title.replace('\n', '')

    def stem_title(self):
        morph = pymorphy2.MorphAnalyzer()
        for word in self.title.split():
            self.stemmed_title.append(morph.parse(word)[0].normal_form)


@logger.catch
class Concurency:
    def __init__(self, site_objects_list, stemmed_request):
        self.site_objects_list = site_objects_list
        self.request = stemmed_request
        self.organic_site_objects_list = list()
        self.super_site_objects_list = list()
        self.direct_site_objects_list = list()
        self.WEIGHTS = dict()
        self.site_age_concurency = ''
        self.site_stem_concurency = ''
        self.site_volume_concurency = ''
        self.site_backlinks_concurency = ''
        self.site_total_concurency = ''
        self.valid_backlinks_rate = 0
        self.direct_upscale = ''

        self.check_site_object_type()

        if len(self.direct_site_objects_list) > 0:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC

        self.calculate_site_age_concurency()
        self.calculate_site_volume_concurency()
        self.calculate_site_stem_concurency()

        while self.valid_backlinks_rate < 0.8:
            self.check_valid_backlinks_sample()
        self.calculate_site_backlinks_concurency()

        logger.info(f'Выборки хватило')
        self.calculate_direct_upscale()
        self.calculate_site_total_concurency()

    def check_site_object_type(self):
        for site_object in self.site_objects_list:
            if site_object.site_type == 'organic':
                self.organic_site_objects_list.append(site_object)
            elif site_object.site_type == 'direct':
                self.direct_site_objects_list.append(site_object)
            else:
                self.super_site_objects_list.append(site_object)

    def calculate_site_age_concurency(self):
        max_age_concurency = 0
        real_age_concurency = 0

        for site_object in self.site_objects_list:
            max_age_concurency += 10 * self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                real_age_concurency += site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]
            else:
                real_age_concurency += 10 * self.WEIGHTS[site_object.position]

        self.site_age_concurency = int(real_age_concurency / max_age_concurency * 100)

    def calculate_site_volume_concurency(self):
        max_volume_concurency = 0
        real_volume_concurency = 0

        for site_object in self.site_objects_list:
            max_volume_concurency += 10000 * self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                real_volume_concurency += site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]
            else:
                real_volume_concurency += 10000 * self.WEIGHTS[site_object.position]

        self.site_volume_concurency = int(real_volume_concurency / max_volume_concurency * 100)

    def calculate_site_stem_concurency(self):
        max_stem_concurency = 0
        real_stem_concurency = 0

        for site_object in self.site_objects_list:
            max_stem_concurency += self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':

                matched_stem_items = len(set(self.request) & set(site_object.content_object.stemmed_title))
                real_stem_concurency += int(matched_stem_items / len(self.request)) * self.WEIGHTS[site_object.position]
            else:
                real_stem_concurency += self.WEIGHTS[site_object.position]

        self.site_stem_concurency = int(real_stem_concurency / max_stem_concurency * 100)

    def check_valid_backlinks_sample(self):
        valid_backlinks = 0
        limit_for_validation = 0.8
        domains_amount = len(self.site_objects_list)

        for site_object in self.site_objects_list:
            try:
                if site_object.domain_object.backlinks > 0:
                    valid_backlinks += 1
            except:
                print('STOP')

        valid_backlinks_rate = valid_backlinks / domains_amount
        self.valid_backlinks_rate = valid_backlinks_rate
        logger.info(f'Данные есть о {valid_backlinks} из {domains_amount} ({int(valid_backlinks_rate * 100)}%)')
        if valid_backlinks_rate < limit_for_validation:
            logger.info(f'Выборки не хватило, начинаю сбор заново')
            time.sleep(10)
            for site_object in self.site_objects_list:
                if site_object.domain_object.backlinks == 0:
                    site_object.domain_object.check_data_in_database()

    def calculate_site_backlinks_concurency(self):
        max_backlinks_concurency = 0
        real_backlinks_concurency = 0
        maximum_backlinks = 500

        for site_object in self.site_objects_list:
            max_backlinks_concurency += 100 * self.WEIGHTS[site_object.position]
            if site_object.domain_object.backlinks > maximum_backlinks:
                site_object.domain_object.backlinks = maximum_backlinks
            real_backlinks_concurency += int(
                site_object.domain_object.backlinks / maximum_backlinks * 100 * self.WEIGHTS[site_object.position])
        self.site_backlinks_concurency = int(real_backlinks_concurency / max_backlinks_concurency * 100)

    def calculate_direct_upscale(self):
        direct_upscale = -35

        for site_object in self.site_objects_list:
            if site_object.site_type == 'direct':
                if site_object.position == '1':
                    direct_upscale += 13.0
                    direct_upscale = round(direct_upscale, 2)
                elif site_object.position == '2':
                    direct_upscale += 9.0
                    direct_upscale = round(direct_upscale, 2)
                elif site_object.position == '3':
                    direct_upscale += 6.0
                    direct_upscale = round(direct_upscale, 2)
                elif site_object.position == '4':
                    direct_upscale += 4.0
                    direct_upscale = round(direct_upscale, 2)
                else:
                    direct_upscale += float(0.6)
                    direct_upscale = round(direct_upscale, 2)
                logger.debug(f'Директ обнаружен на позиции {site_object.position}, текущий upscale = {direct_upscale}')

        self.direct_upscale = direct_upscale

    def calculate_site_total_concurency(self):
        total_difficulty = int(
            self.site_age_concurency * IMPORTANCE['Возраст сайта'] + self.site_stem_concurency * IMPORTANCE[
                'Стемирование'] + self.site_volume_concurency * IMPORTANCE[
                'Объем статей'] + self.site_backlinks_concurency * IMPORTANCE['Ссылочное'])
        total_difficulty += self.direct_upscale
        self.site_total_concurency = total_difficulty
        logger.info(f'Конкуренция от возраста: {self.site_age_concurency}')
        logger.info(f'Конкуренция от объема: {self.site_volume_concurency}')
        logger.info(f'Конкуренция от стема: {self.site_stem_concurency}')
        logger.info(f'Конкуренция от бэклинков: {self.site_backlinks_concurency}')
        logger.info(f'Модификатор от директа: {self.direct_upscale}')
        logger.info(f'Итоговая конкуренция: {total_difficulty}')


if __name__ == "__main__":
    while True:
        Manager()
        time.sleep(10)