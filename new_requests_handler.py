from conc_settings import *
from multiprocessing import Process, Queue
from threading import Thread
from loguru import logger
import time
import pymorphy2
import requests
from bs4 import BeautifulSoup
import lxml
from urllib.parse import urlparse
import postgres_mode as pm
import re


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

        if len(self.process_list) > 0:
            self.refresh_balance()
            self.delete_requests_from_queue()


        print(f'СОбрано {len(self.process_list)} первичных запросов')

    def get_requests_from_queue(self):
        items = pm.check_in_database('main_handledxml', 'status', 'in work', 4)
        reqs = list()
        for item in items:
            reqs.append(item)

        self.requests = tuple(reqs)


    def make_processes(self):
        self.process_list = [Process(target=Yandex, args=(request, self.q)) for request in self.requests]

    def run_processes(self):
        for process in self.process_list:
            process.start()

    def get_data_from_processes(self):
        for process in self.process_list:
            self.yandex_objects_list.append(self.q.get())

    def refresh_balance(self):
        keys_and_tokens = pm.check_in_database('main_payload', 'balance', 0)
        for item in keys_and_tokens:
            key = item[0]
            r = requests.get(f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={key}&host=yandex.ru&parameterList=').json()
            balance = r['hostLimitsBalance']
            if balance == 0:
                pm.delete_from_database('main_payload', 'balance', '0')
            else:
                pm.update_database('main_payload', 'balance', balance, 'key', key)

    def delete_requests_from_queue(self):
        reqs = list()
        for yandex_object in self.yandex_objects_list:
            if yandex_object['Статус'] == 'backlinks':
                pm.update_database('main_handledxml', 'status', 'pending', 'request', yandex_object['Запрос'])
            else:
                reqs.append(yandex_object['Запрос'])
        reqs = tuple(reqs)
        pm.delete_from_database('main_handledxml', 'request', reqs)


@logger.catch
class Site:
    def __init__(self, position, soup):
        self.start = time.time()
        self.soup = soup[0]
        self.estimated_site_type = soup[1]
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

        if self.estimated_site_type == 'unknown':
            try:
                self.get_html()
                self.make_content_object()
                self.make_domain_object()
            except:
                logger.critical(f'Критическая ошибка с доменом {self.domain}')

        self.clean_garbage()

    def clean_garbage(self):
        del self.html
        del self.start
        del self.soup
        del self.domain

    def get_url(self):
        self.url = self.soup.find('url').text

    def get_site_type(self):
        if self.estimated_site_type == 'direct':
            self.site_type = 'direct'
        elif 'yandex.ru' in self.url or 'youtube.com' in self.url or 'wikipedia.org' in self.url:
            self.site_type = 'super'
        else:
            self.site_type = 'organic'

    def get_domain(self):
        if self.estimated_site_type == 'direct':
            self.domain = self.url
        else:
            self.domain = urlparse(self.url)
            self.domain = self.domain.netloc
            self.domain.replace('www.', '')

        while self.domain.count('.') != 1:
            first_dot = self.domain.find('.') + 1
            self.domain = self.domain[first_dot:]

    def is_pdf(self):
        if '.pdf' in self.url:
            return True
        else:
            return False

    def get_html(self):
        try:
            r = requests.get(self.url, headers=HEADERS, verify=False, timeout=10).content
            if not self.is_pdf():
                self.html = BeautifulSoup(r, 'html.parser')
            else:
                self.html = ''
        except:
            logger.critical(f'Не удалось загрузить {self.url}')

    def make_domain_object(self):
        self.domain_object = Domain(self.domain)

    def make_content_object(self):
        self.content_object = Content(self.html, self.site_type, self.domain)

@logger.catch
class Yandex:
    def __init__(self, request, q):


        self.request = request[0]
        self.xml = request[1]
        self.q = q
        self.stemmed_request = list()
        self.page_xml = ''
        self.site_list = list()
        self.site_objects_list = list()
        self.thread_list = ''
        self.concurency_object = ''
        self.result = dict()

        self.start_logging()


        self.stem_request()
        self.get_page_xml()
        self.get_site_list()
        self.clean_garbage()

        self.make_threads()
        self.run_threads()
        self.check_threads()

        self.make_concurency_object()
        self.prepare_result()
        self.add_result_to_database()

        self.q.put(self.result)

    def start_logging(self):
        logger.add("critical.txt", format="{time:HH:mm:ss} {message}", level='CRITICAL', encoding="UTF-8")
        logger.add("important.txt", format="{time:HH:mm:ss} {message}", level='SUCCESS', encoding="UTF-8")
        logger.debug('Класс Yandex создан')
        logger.info(f'Запрос: {self.request}')

    def stem_request(self):
        morph = pymorphy2.MorphAnalyzer()
        for word in self.request.split():
            parsed_word = morph.parse(word)[0]
            type_of_word = str(parsed_word.tag.POS)
            if type_of_word == 'PREP' or type_of_word == 'CONJ' or type_of_word == 'PRCL' or type_of_word == 'INTJ':
                continue
            else:
                self.stemmed_request.append(parsed_word.normal_form)


        #self.stemmed_request = morph.parse(self.request)[0].normal_form.split()
        logger.info(f'Стемированный запрос: {self.stemmed_request}')

    def get_page_xml(self):
        self.page_xml = BeautifulSoup(self.xml, 'lxml')

    def get_site_list(self):
        try:
            top_direct_sites = self.page_xml.find('topads').find_all('query')
        except:
            top_direct_sites = []

        organic_sites = self.page_xml.find_all('doc')

        try:
            bottom_direct_sites = self.page_xml.find('bottomads').find_all('query')
        except:
            bottom_direct_sites = []

        for site in top_direct_sites:
            self.site_list.append((site, 'direct'))

        for site in organic_sites:
            self.site_list.append((site, 'unknown'))

        for site in bottom_direct_sites:
            self.site_list.append((site, 'direct'))

        logger.info(f'Собран список сайтов {self.request}')

    def clean_garbage(self):
        del self.xml
        del self.page_xml

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
        self.concurency_object = Concurency(self.site_objects_list, self.stemmed_request, self.request)

    def prepare_result(self):
        self.result = {
            'Запрос': self.request,
            'Конкуренция по возрасту': self.concurency_object.site_age_concurency,
            'Конкуренция по стему': self.concurency_object.site_stem_concurency,
            'Конкуренция по объему': self.concurency_object.site_volume_concurency,
            'Конкуренция по ссылочному': self.concurency_object.site_backlinks_concurency,
            'Итоговая конкуренция': self.concurency_object.site_total_concurency,
            'Модификатор директ': self.concurency_object.direct_upscale,
            'Статус': self.concurency_object.status,
        }

    def add_result_to_database(self):

        pm.delete_from_database('main_request', 'request', (self.request,))

        if self.concurency_object.site_backlinks_concurency == '':
            self.concurency_object.site_backlinks_concurency = 0

        if self.concurency_object.site_total_concurency == '':
            self.concurency_object.site_total_concurency = 0


        values_to_go = (self.request,
                        self.concurency_object.site_age_concurency,
                        self.concurency_object.site_stem_concurency,
                        self.concurency_object.site_volume_concurency,
                        self.concurency_object.site_backlinks_concurency,
                        self.concurency_object.site_total_concurency,
                        self.concurency_object.direct_upscale,
                        self.concurency_object.status,)
        logger.debug(values_to_go)
        pm.add_to_database_with_autoincrement('main_request', values_to_go)

    def get_scalp(self):
        print(self.page_xml.prettify())


@logger.catch
class Backlinks:
    def __init__(self, domain):
        self.domain = domain
        self.token = ''
        self.request_json = ''
        self.total_backlinks = ''
        self.unique_backlinks = ''
        self.status = ''

        self.get_token()
        self.get_backlinks()

    def get_token(self):
        accounts_with_balance = pm.check_in_database('main_payload', 'balance', 25)
        self.token = accounts_with_balance[0][0]

    def get_backlinks(self):

        self.request_json = requests.get(
            f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={self.token}&host={self.domain}&parameterList=mjDin,mjHin').json()

        if self.request_json['success'] == False:
            logger.info(f'{self.domain} данные не получены по причине {self.request_json["message"]}')
            self.unique_backlinks = 0
            self.total_backlinks = 0
            self.status = 'pending'
        else:
            self.unique_backlinks = int(self.request_json["summary"]["mjDin"])
            self.total_backlinks = int(self.request_json["summary"]["mjHin"])
            self.status = 'complete'
            # logger.info(f'Данные {self.domain} получены. Всего ссылок: {self.request_json["summary"]["mjHin"]}. Уникальных ссылок: {self.request_json["summary"]["mjDin"]}')


@logger.catch
class Domain:
    def __init__(self, domain):
        self.domain = domain
        self.domain_age = ''
        self.backlinks = ''
        self.backlinks_object = ''

        if self.check_data_in_database():
            pass
        else:
            try:
                self.get_domain_age()
                self.make_backlinks_object()
                self.define_unique_backlinks()
                self.add_domain_backlinks_to_database()
            except:
                logger.critical(f'Проблемы с доменом {self.domain}')

    def check_data_in_database(self):
        check = pm.check_in_database('main_domain', 'name', self.domain)

        if check:
            self.domain_age = check[0][1]
            self.backlinks = check[0][2]
            return True
        else:
            return False

    def define_unique_backlinks(self):
        self.backlinks = self.backlinks_object.unique_backlinks

    def add_domain_backlinks_to_database(self):
        values_to_go = (
            self.domain, self.domain_age, self.backlinks,
            self.backlinks_object.total_backlinks, self.backlinks_object.status)
        pm.add_to_database('main_domain', values_to_go)

    def get_domain_age(self):
        URL = f'https://www.nic.ru/whois/?searchWord={self.domain}'
        r = requests.get(URL).content
        soup = BeautifulSoup(r, 'html.parser').text

        if 'Creation Date' in soup:
            start = soup.find('Creation Date') + 15
            finish = start + 4
            item = soup[start:finish]
            self.domain_age = 2020 - int(item)
        elif 'Registered on' in soup:
            start = soup.find('Registered on')
            finish = soup.find('Registry fee')
            item = soup[start:finish].split()[4]
            self.domain_age = 2020 - int(item)
        elif 'created' in soup:
            if '.lv' in self.domain or '.club' in self.domain or '.to' in self.domain or '.ua' in self.domain or '.eu' in self.domain:
                self.valid = False
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
        self.start = time.time()
        self.domain = domain
        self.html = html
        self.site_type = site_type
        self.text = ''
        self.letters_amount = ''
        self.words_amount = ''
        self.title = ''
        self.stemmed_title = list()
        self.valid = True

        if self.site_type == 'organic':
            logger.add("critical.txt", format="{time:HH:mm:ss} {message}", level='CRITICAL', encoding="UTF-8")
            try:
                self.get_text()
                self.count_letters_amount()
                self.get_title()
                self.delete_punctuation_from_title()
                self.stem_title()
            except:
                self.valid = False
                logger.critical(f"Проблема с валидностью контента {self.domain}. ")

        logger.debug(f'Закончил собирать контент сайта {domain} за {time.time() - self.start}')
        self.clean_garbage()

    def get_text(self):
        self.text = self.html.text.replace('\n', '')

    def count_letters_amount(self):
        self.letters_amount = len(self.text)
        # logger.success(f'{self.domain} - реальное кол-во знаков {self.letters_amount}')

        if self.letters_amount > 10000:
            self.letters_amount = 10000


    def get_title(self):
        self.title = self.html.find('title').text
        self.title = self.title.replace('\n', '')



    def delete_punctuation_from_title(self):
        self.title = re.sub(r'[^\w\s]', '', self.title)

    def stem_title(self):
        morph = pymorphy2.MorphAnalyzer()
        for word in self.title.split():
            self.stemmed_title.append(morph.parse(word)[0].normal_form)

    def clean_garbage(self):
        del self.html
        del self.text
        del self.start




@logger.catch
class Concurency:
    def __init__(self, site_objects_list, stemmed_request, req):
        self.site_objects_list = site_objects_list
        self.request = stemmed_request
        self.report_file_name = req
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
        self.status = str()

        self.check_site_object_type()

        if len(self.direct_site_objects_list) > 0:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC

        self.calculate_site_age_concurency()
        self.calculate_site_volume_concurency()
        self.calculate_site_stem_concurency()

        self.check_valid_backlinks_sample()
        self.calculate_direct_upscale()

        if self.valid_backlinks_rate >= 1:
            self.calculate_site_backlinks_concurency()
            logger.info(f'Выборки хватило')
            self.calculate_site_total_concurency()
            self.status = 'ready'
        else:
            logger.info(f'Выборки не хватило ({int(self.valid_backlinks_rate * 100)}%)')
            self.status = 'backlinks'

        self.prepare_report()

    def check_site_object_type(self):
        for site_object in self.site_objects_list:
            if site_object.site_type == 'organic':
                if site_object.content_object.valid:
                    self.organic_site_objects_list.append(site_object)
            elif site_object.site_type == 'direct':
                self.direct_site_objects_list.append(site_object)
            else:
                self.super_site_objects_list.append(site_object)

    def calculate_site_age_concurency(self):
        max_age_concurency = 0
        real_age_concurency = 0

        for site_object in self.site_objects_list:
            try:
                max_age_concurency += 10 * self.WEIGHTS[site_object.position]
                if site_object.site_type == 'organic':
                    real_age_concurency += site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]
                    # Тест модуль
                    # logger.success(f'Сайт: {site_object.content_object.domain}. Возраст сайта {site_object.domain_object.domain_age}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]} из {10 * self.WEIGHTS[site_object.position]}')
                else:
                    real_age_concurency += 10 * self.WEIGHTS[site_object.position]

            except:
                logger.critical(f'В calculate_site_age_concurency срочно нужен дебаг. Проблема с доменом {site_object.content_object.domain}')


        self.site_age_concurency = int(real_age_concurency / max_age_concurency * 100)

    def calculate_site_volume_concurency(self):
        max_volume_concurency = 0
        real_volume_concurency = 0

        for site_object in self.site_objects_list:
            max_volume_concurency += 10000 * self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                if site_object.content_object.valid:
                    real_volume_concurency += site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]
                else:
                    real_volume_concurency += 5000 * self.WEIGHTS[site_object.position]
                #тест модуль
                #logger.success(f'Сайт: {site_object.content_object.domain}. Объем статьи {site_object.content_object.letters_amount}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}')
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
                #тест модуль
                #test = matched_stem_items / len(self.request)
                #test2 = matched_stem_items / len(self.request) * self.WEIGHTS[site_object.position]
                #logger.success(f'Запрос: {self.request}. Стемированный тайтл: {site_object.content_object.stemmed_title}. Кол-во совпадений: {matched_stem_items}. Кэф: {test}. Оценка конкуренции {test2} из максимальных {self.WEIGHTS[site_object.position]}')
            else:
                real_stem_concurency += self.WEIGHTS[site_object.position]

        self.site_stem_concurency = int(real_stem_concurency / max_stem_concurency * 100)

    def check_valid_backlinks_sample(self):
        valid_backlinks = 0
        limit_for_validation = 0.8
        domains_amount = len(self.organic_site_objects_list) + len(self.super_site_objects_list)

        for site_object in self.site_objects_list:
            try:
                if site_object.domain_object.backlinks > 0:
                    valid_backlinks += 1
            except:
                pass

        valid_backlinks_rate = valid_backlinks / domains_amount
        self.valid_backlinks_rate = valid_backlinks_rate
        logger.info(f'Данные есть о {valid_backlinks} из {domains_amount} ({int(valid_backlinks_rate * 100)}%)')


    def calculate_site_backlinks_concurency(self):
        max_backlinks_concurency = 0
        real_backlinks_concurency = 0
        maximum_backlinks = 500

        for site_object in self.site_objects_list:
            try:
                if site_object.domain_object.backlinks > maximum_backlinks:
                    site_object.domain_object.backlinks = maximum_backlinks
                real_backlinks_concurency += site_object.domain_object.backlinks * self.WEIGHTS[site_object.position]
                max_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]
                #Тест модуль
                # logger.success(f'Сайт: {site_object.content_object.domain}. Ссылок: {site_object.domain_object.backlinks}. Кэф: {site_object.domain_object.backlinks / maximum_backlinks}. Сложность: {int(site_object.domain_object.backlinks / maximum_backlinks * 100 * self.WEIGHTS[site_object.position])} из {100 * self.WEIGHTS[site_object.position]}')
            except:
                real_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]
                max_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]
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
        self.site_total_concurency = int(total_difficulty)
        logger.info(f'Конкуренция от возраста: {self.site_age_concurency}')
        logger.info(f'Конкуренция от объема: {self.site_volume_concurency}')
        logger.info(f'Конкуренция от стема: {self.site_stem_concurency}')
        logger.info(f'Конкуренция от бэклинков: {self.site_backlinks_concurency}')
        logger.info(f'Модификатор от директа: {self.direct_upscale}')
        logger.info(f'Итоговая конкуренция: {total_difficulty}')

    def prepare_report(self):
        file = open(f'./reports/{self.report_file_name}.txt', 'a', encoding='utf-8')

        file.write(f'Стемированный запрос: {self.request}\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от возраста сайта:\n')
        real_concurency = int()
        max_concurency = int()

        for site_object in self.site_objects_list:
            try:
                file.write(f'Сайт: {site_object.content_object.domain}. Возраст сайта {site_object.domain_object.domain_age}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]} из {10 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]
                max_concurency += 10 * self.WEIGHTS[site_object.position]
            except:
                file.write(f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10 * self.WEIGHTS[site_object.position]} из {10 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += 10 * self.WEIGHTS[site_object.position]
                max_concurency += 10 * self.WEIGHTS[site_object.position]
        file.write(f'Уровень конкуренции от возраста: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_age_concurency}\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от объема контента:\n')
        real_concurency = int()
        max_concurency = int()
        for site_object in self.site_objects_list:
            try:

                if site_object.content_object.valid:
                    if site_object.site_type == 'super':
                        file.write(f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                        real_concurency += 10000 * self.WEIGHTS[site_object.position]
                        max_concurency += 10000 * self.WEIGHTS[site_object.position]
                    else:
                        file.write(f'Сайт: {site_object.content_object.domain}. Объем статьи {site_object.content_object.letters_amount}. Находится на {site_object.position}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                        real_concurency += site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]
                        max_concurency += 10000 * self.WEIGHTS[site_object.position]
                else:
                    file.write(f'Сайт: {site_object.content_object.domain}. Контент не валиден (5000 знаков по умолчанию). Находится на {site_object.position}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {5000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                    real_concurency += 5000 * self.WEIGHTS[site_object.position]
                    max_concurency += 10000 * self.WEIGHTS[site_object.position]
            except:
                file.write(f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += 10000 * self.WEIGHTS[site_object.position]
                max_concurency += 10000 * self.WEIGHTS[site_object.position]
        file.write(f'Уровень конкуренции от объема контента: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_volume_concurency}\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от стема:\n')
        real_concurency = int()
        max_concurency = int()

        for site_object in self.site_objects_list:
            max_concurency += self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                matched_stem_items = len(set(self.request) & set(site_object.content_object.stemmed_title))
                real_concurency += int(matched_stem_items / len(self.request)) * self.WEIGHTS[site_object.position]
                test = matched_stem_items / len(self.request)
                test2 = matched_stem_items / len(self.request) * self.WEIGHTS[site_object.position]
                file.write(f'Сайт: {site_object.content_object.domain}. Запрос: {self.request}. Стемированный тайтл: {site_object.content_object.stemmed_title}. Кол-во совпадений: {matched_stem_items}.Находится на {site_object.position} месте. Процент совпадений: {round(test, 2)}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {test2} из максимальных {self.WEIGHTS[site_object.position]}.\n')
            else:
                file.write(f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {self.WEIGHTS[site_object.position]} из {self.WEIGHTS[site_object.position]}\n')
                real_concurency += self.WEIGHTS[site_object.position]
        file.write(f'Уровень конкуренции от стема: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_stem_concurency}\n')
        file.write('----------------------------------------\n')
        file.write('Апскейл от директа:\n')

        direct_upscale = -35
        for site_object in self.site_objects_list:
            if site_object.site_type == 'direct':
                if site_object.position == '1':
                    direct_upscale += 13.0
                    direct_upscale = round(direct_upscale, 2)
                    file.write(f'Direct обнаружен на позиции {site_object.position}. Уровень вырос на 13\n')
                elif site_object.position == '2':
                    direct_upscale += 9.0
                    direct_upscale = round(direct_upscale, 2)
                    file.write(f'Direct обнаружен на позиции {site_object.position}. Уровень вырос на 9\n')
                elif site_object.position == '3':
                    direct_upscale += 6.0
                    direct_upscale = round(direct_upscale, 2)
                    file.write(f'Direct обнаружен на позиции {site_object.position}. Уровень вырос на 6\n')
                elif site_object.position == '4':
                    direct_upscale += 4.0
                    direct_upscale = round(direct_upscale, 2)
                    file.write(f'Direct обнаружен на позиции {site_object.position}. Уровень вырос на 4\n')
                else:
                    direct_upscale += float(0.6)
                    direct_upscale = round(direct_upscale, 2)
                    file.write(f'Direct обнаружен на позиции {site_object.position}. Уровень вырос на 0.6\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от бэклинков:\n')
        real_concurency = int()
        max_concurency = int()

        if self.status == 'ready':
            for site_object in self.site_objects_list:
                max_concurency += 500 * self.WEIGHTS[site_object.position]
                if site_object.site_type == 'organic':
                    real_concurency += site_object.domain_object.backlinks * self.WEIGHTS[site_object.position]
                    file.write(f'Сайт: {site_object.content_object.domain}. Количество бэклинков: {site_object.domain_object.backlinks}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]} Сложность повысилась на {site_object.domain_object.backlinks * self.WEIGHTS[site_object.position]} из {500 * self.WEIGHTS[site_object.position]}\n')
                else:
                    real_concurency += 500 * self.WEIGHTS[site_object.position]
                    file.write(f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {500 * self.WEIGHTS[site_object.position]} из {500 * self.WEIGHTS[site_object.position]}\n')
            file.write(f'Уровень конкуренции от бэклинков: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_backlinks_concurency}\n')

            file.write(f'Итоговая конкуренция:\n')
            total_difficulty = int(
                self.site_age_concurency * IMPORTANCE['Возраст сайта'] + self.site_stem_concurency * IMPORTANCE[
                    'Стемирование'] + self.site_volume_concurency * IMPORTANCE[
                    'Объем статей'] + self.site_backlinks_concurency * IMPORTANCE['Ссылочное'])

            file.write(f"От возраста: {self.site_age_concurency} * {IMPORTANCE['Возраст сайта']} = {self.site_age_concurency * IMPORTANCE['Возраст сайта']}\n")
            file.write(f"От стема: {self.site_stem_concurency} * {IMPORTANCE['Стемирование']} = {self.site_stem_concurency * IMPORTANCE['Стемирование']}\n")
            file.write(f"От объема: {self.site_volume_concurency} * {IMPORTANCE['Объем статей']} = {self.site_volume_concurency * IMPORTANCE['Объем статей']}\n")
            file.write(f"От ссылочного: {self.site_backlinks_concurency} * {IMPORTANCE['Ссылочное']} = {self.site_backlinks_concurency * IMPORTANCE['Ссылочное']}\n")
            file.write(f'До вычета direct upscale: {total_difficulty}\n')

            total_difficulty += direct_upscale
            file.write(f'После вычета direct upscale ({direct_upscale}): {total_difficulty}\n')



        else:
            file.write('Бэклинков недостаточно\n')
        file.close()
        print('ya')

if __name__ == "__main__":
    while True:
        Manager()
        time.sleep(10)