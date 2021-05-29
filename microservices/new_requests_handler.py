from microservices.conc_settings import *
from multiprocessing import Process, Queue
from threading import Thread
from loguru import logger
import time
import pymorphy2
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from microservices import postgres_mode as pm
import re
from dataclasses import dataclass


@dataclass
class RequestDataSet:
    id: int
    text: str
    xml: str
    xml_status: str
    region_id: int


@dataclass
class SiteDataSet:
    html: str
    type: str
    order_on_page: int

@logger.catch
class Manager:
    def __init__(self):
        self.requests = list()
        self.yandex_objects_list = list()
        self.process_list = list()
        self.q = Queue()

        self.get_requests_from_queue()
        self.run_processes()

        if len(self.process_list) > 0:
            self.refresh_balance()
            self.delete_requests_from_queue()

        print(f'СОбрано {len(self.process_list)} первичных запросов')

    def get_requests_from_queue(self):
        """
        Метод берет данные из БД и кладет их в датасет, который будет дополняться в ходе выполнения инструкций.
        Так как для каждого датасета будет выделен отдельный процесс, лимит ограничен количеством ядер процессора
        """

        sql = ("SELECT request_id, text, xml, xml.status, xml.region_id "
               "FROM concurent_site.main_handledxml xml "
               "INNER JOIN concurent_site.main_request req "
               "ON (xml.request_id = req.id) "
               "WHERE xml.status = 'in work' "
               f"LIMIT {core_number};")

        database_return = pm.custom_request_to_database_with_return(sql)

        for data in database_return:
            request_dataset = RequestDataSet(id=data[0], text=data[1], xml=data[2],
                                             xml_status=data[3], region_id=data[4])

            self.requests.append(request_dataset)

        self.requests = tuple(self.requests)

    def run_processes(self):
        """
        Создает процессы, кладет в каждый из них датасет и объект класса Queue для извлечения данных.
        Затем запускает эти процессы и ожидает получение данных от Queue
        """
        self.make_processes()
        self.start_processes()
        self.get_data_from_processes()

    def make_processes(self):
        self.process_list = [Process(target=Yandex, args=(request, self.q)) for request in self.requests]

    def start_processes(self):
        for process in self.process_list:
            process.start()

    def get_data_from_processes(self):
        for process in self.process_list:
            self.yandex_objects_list.append(self.q.get())

    @staticmethod
    def _get_keys_list():
        sql = ('SELECT key '
               'FROM concurent_site.main_payload;')

        return pm.custom_request_to_database_with_return(sql)

    @staticmethod
    def _get_balance(key):
        balance_request_return = requests.get(
            f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={key}&host=yandex.ru&parameterList=').json()
        return balance_request_return['hostLimitsBalance']

    @staticmethod
    def _delete_checktrust_zero_balance_accounts(zero_balance_accounts_count):
        if zero_balance_accounts_count:
            sql = ('DELETE FROM concurent_site.main_payload '
                   'WHERE balance = 0;')

            pm.custom_request_to_database_without_return(sql)

    @staticmethod
    def _update_checktrust_api_balance_accounts(key, balance):
        sql = ("UPDATE concurent_site.main_payload "
               f"SET key = '{key}' "
               f"balance = {balance};")

        pm.custom_request_to_database_without_return(sql)

    def refresh_balance(self):
        """
        У меня тут маленький стартап, так что приходится экономить :)
        Часть данных о конкуренции получается с помощью API сервиса checktrust. Но полноценная подписка очень дорогая
        Так что на время тестирования приходится абузить триал аккаунты. Этот метод проверяет баланс на триал аккаунтах
        и удаляет те, на которых нулевой баланс.
        """
        keys_list = self._get_keys_list()
        zero_balance_accounts_count = 0
        for key in keys_list:
            balance = self._get_balance(key)
            if balance == 0:
                zero_balance_accounts_count += 1
            else:
                self._update_checktrust_api_balance_accounts(key, balance)

        self._delete_checktrust_zero_balance_accounts(zero_balance_accounts_count)

    def delete_requests_from_queue(self):
        for yandex_object in self.yandex_objects_list:
            if yandex_object['Статус'] == 'backlinks':
                sql = f"UPDATE concurent_site.main_handledxml SET status = 'pending' WHERE request_id = {yandex_object['ID запроса']};"
                pm.custom_request_to_database_without_return(sql)
            else:
                sql = f"UPDATE concurent_site.main_handledxml SET status = 'conf' WHERE request_id = {yandex_object['ID запроса']};"
                pm.custom_request_to_database_without_return(sql)

@logger.catch
class Site:
    def __init__(self, position, soup):
        self.start = time.time()
        self.soup = soup[0]
        self.estimated_site_type = soup[1]
        self.position = position
        self.url = str()
        self.domain = str()
        self.site_type = str()
        self.html = str()
        self.domain_object = str()
        self.content_object = str()

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
        if self.estimated_site_type == 'direct' or 'yabs.yandex.ru' in self.url:
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

        if 'Турбо-страница' in self.domain:
            self.domain = 'yandex.ru'

        if self.domain.count('.') == 0:
            self.domain = self.domain + '.ru'

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
            r = requests.get(self.url, headers=HEADERS, verify=False, timeout=15).content
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
        print('ya')
        self.request_id = request.id
        self.request_text = request.text
        self.xml_text = request.xml
        self.region_id = request.region_id
        self.q = q
        self.stemmed_request = list()
        self.site_list = list()
        self.site_objects_list = list()
        self.thread_list = str()
        self.concurency_object = str()
        self.result = dict()
        self.request_views = int()

        self.start_logging()

        self.stem_request()

        self.parse_xml_text_with_bs4()
        self.get_request_views()
        self.get_site_list()

        self.clean_garbage()

        self.make_threads()
        self.run_threads()
        self.check_threads()

        self.make_concurency_object()
        self.prepare_result()
        self.add_result_to_database()

        self.q.put(self.result)

    def get_request_views(self):
        """
        Примерно в ~50% XML ответах есть тег <displayed>, который показывает количество показов запроса в месяц.
        """
        try:
            self.request_views = int(self.xml_text.find('displayed').text)
        except:
            self.request_views = 0

    def start_logging(self):
        logger.add("critical.txt", format="{time:HH:mm:ss} {message}", level='CRITICAL', encoding="UTF-8")
        logger.add("important.txt", format="{time:HH:mm:ss} {message}", level='SUCCESS', encoding="UTF-8")
        logger.debug('Класс Yandex создан')
        logger.info(f'Запрос: {self.request_text}')

    def _is_functional_part_of_speech(self, part_of_speech):
        if part_of_speech == 'PREP' or part_of_speech == 'CONJ' or part_of_speech == 'PRCL' or part_of_speech == 'INTJ':
            return True

    def stem_request(self):
        """
        Стемироание - приведение слова к его изначальной форме. Например, слова "покупка" и "купить" будет приведены
        к слову "купить". Это очень полезно для оценки конкуренции по вхождению ключевых слов в заголовок страницы.
        Метод _is_functional_part_of_speech отсекает служебные части речи. Они не нужны.
        """
        morpher = pymorphy2.MorphAnalyzer()
        for word in self.request_text.split():
            stemed_word = morpher.parse(word)
            the_best_form_of_stemed_word = stemed_word[0]
            part_of_speech = str(the_best_form_of_stemed_word.tag.POS)
            if not self._is_functional_part_of_speech(part_of_speech):
                self.stemmed_request.append(the_best_form_of_stemed_word.normal_form)

        logger.info(f'Стемированный запрос: {self.stemmed_request}')

    def parse_xml_text_with_bs4(self):
        self.xml_text = BeautifulSoup(self.xml_text, 'lxml')

    def _parse_url_data_from_page_xml(self, xml_tag, ad_tag=''):
        """
        Из объекта BS4 парсится html код, содержащий базовую информацию о сайте
        """
        if ad_tag:
            text = self.xml_text.find(ad_tag)
            if text:
                return text.find_all(xml_tag)
            else:
                return []
        else:
            return self.xml_text.find_all(xml_tag)

    def _make_datasets(self, html_list, site_type):

        order_on_page = self._prepare_site_data.order_on_page
        for site in html_list:
            site_dataset = SiteDataSet(html=site, type=site_type, order_on_page=order_on_page)
            order_on_page += 1
            self.site_list.append(site_dataset)

    def _prepare_site_data(self, top_direct_sites, organic_sites, bottom_direct_sites):

        self._prepare_site_data.order_on_page = 1
        self._make_datasets(top_direct_sites, 'direct')

        for site in top_direct_sites:
            site_dataset = SiteDataSet(html=site, type='direct', order_on_page=order_on_page)
            order_on_page += 1
            self.site_list.append(site_dataset)

        for site in organic_sites:
            site_dataset = SiteDataSet(html=site, type='organic', order_on_page=order_on_page)
            order_on_page += 1
            self.site_list.append(site_dataset)

        for site in bottom_direct_sites:
            site_dataset = SiteDataSet(html=site, type='direct', order_on_page=order_on_page)
            order_on_page += 1
            self.site_list.append(site_dataset)

    def get_site_list(self):
        top_direct_sites = self._parse_url_data_from_page_xml('query', 'topads')
        organic_sites = self._parse_url_data_from_page_xml('doc')
        bottom_direct_sites = self._parse_url_data_from_page_xml('query', 'bottomads')

        self._prepare_site_data(top_direct_sites, organic_sites, bottom_direct_sites)

        logger.info(f'Собран список сайтов {self.request}')

    def clean_garbage(self):
        del self.xml

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
            'Средний возраст': self.concurency_object.average_site_age,
            'Средний объем': self.concurency_object.average_site_volume,
            'Средние уник бэклинки': self.concurency_object.average_unique_backlinks,
            'Средние тотал бэклинки': self.concurency_object.average_total_backlinks,
            'Гео': self.geo,
            'Показов запроса': self.request_views,
            'ID запроса': self.request_id
        }

    def add_result_to_database(self):

        if self.concurency_object.site_backlinks_concurency == '':
            self.concurency_object.site_backlinks_concurency = 0

        if self.concurency_object.site_total_concurency == '':
            self.concurency_object.site_total_concurency = 0

        pm.custom_request_to_database_without_return(
            f"UPDATE concurent_site.main_request SET "
            f"site_age_concurency = {self.concurency_object.site_age_concurency}, "
            f"site_stem_concurency = {self.concurency_object.site_stem_concurency}, "
            f"site_volume_concurency = {self.concurency_object.site_volume_concurency}, "
            f"site_backlinks_concurency = {self.concurency_object.site_backlinks_concurency}, "
            f"site_total_concurency = {self.concurency_object.site_total_concurency}, "
            f"direct_upscale = {self.concurency_object.direct_upscale}, "
            f"status = '{self.concurency_object.status}', "
            f"site_direct_concurency = {self.concurency_object.site_direct_concurency}, "
            f"site_seo_concurency = {self.concurency_object.site_seo_concurency}, "
            f"request_views = {self.request_views}, "
            f"average_age = {self.concurency_object.average_site_age}, "
            f"average_volume = {self.concurency_object.average_site_volume}, "
            f"average_total_backlinks = {self.concurency_object.average_total_backlinks}, "
            f"average_unique_backlinks = {self.concurency_object.average_unique_backlinks}, "
            f"vital_sites = '{self.concurency_object.vital_domains}', "
            f"vital_sites_count = {self.concurency_object.vital_domains_amount} "
            f"WHERE request_id = {self.request_id}"
        )


@logger.catch
class Backlinks:
    def __init__(self, domain):
        self.domain = domain
        self.token = str()
        self.request_json = str()
        self.total_backlinks = str()
        self.unique_backlinks = str()
        self.status = str()
        self.domain_group = 0

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

            if self.unique_backlinks >= 10000 or self.total_backlinks >= 30000:
                self.domain_group = 1


@logger.catch
class Domain:
    def __init__(self, domain):
        self.domain = domain
        self.domain_age = str()
        self.unique_backlinks = str()
        self.total_backlinks = str()
        self.backlinks_object = str()
        self.domain_group = int()

        if self.check_data_in_database():
            pass
        else:
            try:
                self.get_domain_age()
                self.make_backlinks_object()
                self.domain_group = self.backlinks_object.domain_group
                self.define_backlinks_amount()
                self.add_domain_backlinks_to_database()
            except:
                logger.critical(f'Проблемы с доменом {self.domain}')

    def check_data_in_database(self):
        check = pm.check_in_database('main_domain', 'name', self.domain)

        if check:
            self.domain_age = check[0][1]
            self.unique_backlinks = check[0][2]
            self.total_backlinks = check[0][3]
            self.domain_group = check[0][5]
            return True
        else:
            return False

    def define_backlinks_amount(self):
        self.unique_backlinks = self.backlinks_object.unique_backlinks
        self.total_backlinks = self.backlinks_object.total_backlinks

    def add_domain_backlinks_to_database(self):
        values_to_go = (
            self.domain, self.domain_age, self.unique_backlinks,
            self.total_backlinks, self.backlinks_object.status, self.backlinks_object.domain_group)
        pm.add_to_database('main_domain', values_to_go)

    def get_domain_age(self):
        URL = f'https://www.nic.ru/whois/?searchWord={self.domain}'
        r = requests.get(URL).content
        soup = BeautifulSoup(r, 'html.parser').text

        try:
            if 'Creation Date' in soup:
                start = soup.find('Creation Date') + 15
                finish = start + 4
                item = soup[start:finish]
                self.domain_age = 2021 - int(item)
            elif 'Registered on' in soup:
                start = soup.find('Registered on')
                finish = soup.find('Registry fee')
                item = soup[start:finish].split()[4]
                self.domain_age = 2021 - int(item)
            elif 'created' in soup:
                if '.lv' in self.domain or '.club' in self.domain or '.to' in self.domain or '.ua' in self.domain or '.eu' in self.domain:
                    self.valid = False
                    self.domain_age = 5
                else:
                    start = soup.find('created') + 8
                    finish = start + 4
                    item = soup[start:finish]
                    self.domain_age = 2021 - int(item)
        except:
            print(f'Возраст домена {self.domain} определен неправильно')
            self.domain_age = 5



    def make_backlinks_object(self):
        self.backlinks_object = Backlinks(self.domain)


@logger.catch
class Content:
    def __init__(self, html, site_type, domain):
        self.start = time.time()
        self.domain = domain
        self.html = html
        self.site_type = site_type
        self.text = str()
        self.letters_amount = str()
        self.words_amount = str()
        self.title = str()
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
        self.super_ads_amount = int()
        self.WEIGHTS = dict()
        self.importance = dict()
        self.site_age_concurency = int()
        self.site_stem_concurency = int()
        self.site_volume_concurency = int()
        self.site_backlinks_concurency = int()
        self.site_total_concurency = int()
        self.site_seo_concurency = int()
        self.site_direct_concurency = int()
        self.valid_backlinks_rate = 0
        self.direct_upscale = int()
        self.status = str()

        self.average_site_age = int()
        self.average_site_volume = int()
        self.average_unique_backlinks = int()
        self.average_total_backlinks = int()

        self.vital_domains = list()
        self.vital_domains_amount = int()

        self.check_site_object_type()

        if len(self.direct_site_objects_list) > 0:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC

        self.calculate_site_stem_concurency()
        if self.check_is_absourd_request():
            self.importance = ABSURD_STEM_IMPORTANCE
        else:
            self.importance = STANDART_IMPORTANCE

        self.calculate_site_age_concurency()
        self.calculate_site_volume_concurency()

        self.check_valid_backlinks_sample()
        self.calculate_direct_upscale()
        self.calculate_direct_concurency()

        if self.valid_backlinks_rate >= 1:
            self.calculate_site_backlinks_concurency()
            logger.info(f'Выборки ({self.request}) хватило')
            self.calculate_site_total_concurency()
            self.status = 'ready'
        else:
            logger.info(f'Выборки не хватило ({int(self.valid_backlinks_rate * 100)}%)')
            self.status = 'backlinks'

        self.prepare_report()

        self.convert_vital_domains_to_sting()

    def check_site_object_type(self):
        for site_object in self.site_objects_list:
            if site_object.site_type == 'organic':
                if site_object.content_object.valid:
                    self.organic_site_objects_list.append(site_object)
            elif site_object.site_type == 'direct':
                if int(site_object.position) <= 4:
                    self.super_ads_amount += 1
                self.direct_site_objects_list.append(site_object)
            else:
                self.super_site_objects_list.append(site_object)

    def calculate_site_age_concurency(self):
        max_age_concurency = 0
        real_age_concurency = 0
        total_site_age = 0

        for site_object in self.site_objects_list:
            try:
                max_age_concurency += 10 * self.WEIGHTS[site_object.position]
                if site_object.site_type == 'organic':
                    site_age = site_object.domain_object.domain_age
                    total_site_age += site_age

                    if site_age > 10:
                        site_age = 10

                    real_age_concurency += site_age * self.WEIGHTS[site_object.position]
                else:
                    real_age_concurency += 10 * self.WEIGHTS[site_object.position]

            except:
                logger.critical(
                    f'В calculate_site_age_concurency срочно нужен дебаг. Проблема с доменом {site_object.content_object.domain}')

        self.site_age_concurency = int(real_age_concurency / max_age_concurency * 100)
        self.average_site_age = int(total_site_age / len(self.organic_site_objects_list))

    def calculate_site_volume_concurency(self):
        max_volume_concurency = 0
        real_volume_concurency = 0
        maximum_letters = 10000

        total_letters = 0

        for site_object in self.site_objects_list:
            max_volume_concurency += 10000 * self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                if site_object.content_object.valid:
                    letters_amount = site_object.content_object.letters_amount
                    total_letters += letters_amount

                    if letters_amount > maximum_letters:
                        letters_amount = maximum_letters

                    real_volume_concurency += letters_amount * self.WEIGHTS[site_object.position]
                else:
                    real_volume_concurency += 5000 * self.WEIGHTS[site_object.position]
            else:
                real_volume_concurency += 10000 * self.WEIGHTS[site_object.position]

        self.site_volume_concurency = int(real_volume_concurency / max_volume_concurency * 100)
        self.average_site_volume = int(total_letters / len(self.organic_site_objects_list))

    def calculate_site_stem_concurency(self):
        max_stem_concurency = 0
        real_stem_concurency = 0

        for site_object in self.site_objects_list:
            max_stem_concurency += self.WEIGHTS[site_object.position]
            if site_object.site_type == 'organic':
                matched_stem_items = self.count_matched_stem_items(site_object.content_object.stemmed_title)
                real_stem_concurency += matched_stem_items / len(self.request) * self.WEIGHTS[site_object.position]
            else:
                real_stem_concurency += self.WEIGHTS[site_object.position]

        self.site_stem_concurency = int(real_stem_concurency / max_stem_concurency * 100)

    def count_matched_stem_items(self, stemmed_title):
        matched_stem_items = 0

        for stemmed_request_word in self.request:
            for stemmed_title_word in stemmed_title:
                if stemmed_request_word in stemmed_title_word:
                    matched_stem_items += 1
                    print(f'{stemmed_request_word} in {stemmed_title_word}')

        return matched_stem_items



    def check_is_absourd_request(self):
        if self.site_stem_concurency < 30:
            print('Запрос абсурдный')
            return True

    def check_valid_backlinks_sample(self):
        valid_backlinks = 0
        domains_amount = len(self.organic_site_objects_list) + len(self.super_site_objects_list)

        for site_object in self.site_objects_list:
            try:
                if site_object.domain_object.unique_backlinks > 0:
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

        total_total_backlinks = 0
        total_unique_backlinks = 0

        file = open(f'./reports/backs.txt', 'a', encoding='utf-8')
        for site_object in self.site_objects_list:
            try:
                unique_backlinks = site_object.domain_object.unique_backlinks
                total_backlinks = site_object.domain_object.total_backlinks
                domain_group = site_object.domain_object.domain_group

                if domain_group:
                    file.write(f'Сайт: {site_object.domain_object.domain}. Уников: {site_object.domain_object.unique_backlinks}. Тотал: {site_object.domain_object.total_backlinks}. Витальный сайт, в статистику не попал \n')
                else:
                    file.write(f'Сайт: {site_object.domain_object.domain}. Уников: {site_object.domain_object.unique_backlinks}. Тотал: {site_object.domain_object.total_backlinks}. НЕ витальный сайт\n')


                if site_object.site_type == 'organic':
                    if domain_group != 1:
                        total_unique_backlinks += unique_backlinks
                        total_total_backlinks += total_backlinks
                    else:
                        if int(site_object.position) + self.super_ads_amount <= 10:
                            self.vital_domains.append(site_object.domain_object.domain)
                elif site_object.site_type == 'super':
                    if int(site_object.position) + self.super_ads_amount <= 10:
                        self.vital_domains.append(site_object.domain_object.domain)

                if unique_backlinks > maximum_backlinks:
                    unique_backlinks = maximum_backlinks
                real_backlinks_concurency += unique_backlinks * self.WEIGHTS[site_object.position]
                max_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]
            except:
                real_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]
                max_backlinks_concurency += 500 * self.WEIGHTS[site_object.position]

        self.site_backlinks_concurency = int(real_backlinks_concurency / max_backlinks_concurency * 100)
        self.average_total_backlinks = int(total_total_backlinks / len(self.organic_site_objects_list))
        self.average_unique_backlinks = int(total_unique_backlinks / len(self.organic_site_objects_list))
        file.write(f'Среднее тотал {self.average_total_backlinks}, среднее уник {self.average_unique_backlinks}')
        file.close()

    def calculate_direct_upscale(self):
        direct_upscale = 0
        direct_sites = 0

        for site_object in self.site_objects_list:
            if site_object.site_type == 'direct':
                direct_sites += 1

        logger.debug(f'Всего {direct_sites} сайтов в директе')

        if direct_sites >= 5:
            direct_upscale += 8
            direct_sites -= 5

            if direct_sites == 4:
                direct_upscale += 27
            elif direct_sites == 3:
                direct_upscale += 23
            elif direct_sites == 2:
                direct_upscale += 17
            elif direct_sites == 1:
                direct_upscale += 8
        else:
            if direct_sites == 5:
                direct_upscale += 8
            elif direct_sites == 4:
                direct_upscale += 6.4
            elif direct_sites == 3:
                direct_upscale += 4.8
            elif direct_sites == 2:
                direct_upscale += 3.2
            elif direct_sites == 1:
                direct_upscale += 1.6

        logger.debug(f'Upscale = {direct_upscale}')

        self.direct_upscale = direct_upscale

    def calculate_site_total_concurency(self):
        total_difficulty = int(
            self.site_age_concurency * self.importance['Возраст сайта'] + self.site_stem_concurency * self.importance[
                'Стемирование'] + self.site_volume_concurency * self.importance[
                'Объем статей'] + self.site_backlinks_concurency * self.importance['Ссылочное'])
        self.site_seo_concurency = total_difficulty
        total_difficulty += self.direct_upscale
        self.site_total_concurency = int(total_difficulty)
        logger.info(f'Конкуренция от возраста: {self.site_age_concurency}')
        logger.info(f'Конкуренция от объема: {self.site_volume_concurency}')
        logger.info(f'Конкуренция от стема: {self.site_stem_concurency}')
        logger.info(f'Конкуренция от бэклинков: {self.site_backlinks_concurency}')
        logger.info(f'Модификатор от директа: {self.direct_upscale}')
        logger.info(f'Итоговая конкуренция: {total_difficulty}')

    def calculate_direct_concurency(self):
        self.site_direct_concurency = int(self.direct_upscale / 35 * 100)

    def prepare_report(self):
        file = open(f'./reports/{self.report_file_name}.txt', 'a', encoding='utf-8')

        file.write(f'Стемированный запрос: {self.request}\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от возраста сайта:\n')
        real_concurency = int()
        max_concurency = int()

        for site_object in self.site_objects_list:
            try:
                file.write(
                    f'Сайт: {site_object.content_object.domain}. Возраст сайта {site_object.domain_object.domain_age}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]} из {10 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += site_object.domain_object.domain_age * self.WEIGHTS[site_object.position]
                max_concurency += 10 * self.WEIGHTS[site_object.position]
            except:
                file.write(
                    f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10 * self.WEIGHTS[site_object.position]} из {10 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += 10 * self.WEIGHTS[site_object.position]
                max_concurency += 10 * self.WEIGHTS[site_object.position]
        file.write(
            f'Уровень конкуренции от возраста: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_age_concurency}\n')
        file.write('----------------------------------------\n')
        file.write(f'Конкуренция от объема контента:\n')
        real_concurency = int()
        max_concurency = int()
        for site_object in self.site_objects_list:
            try:

                if site_object.content_object.valid:
                    if site_object.site_type == 'super':
                        file.write(
                            f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                        real_concurency += 10000 * self.WEIGHTS[site_object.position]
                        max_concurency += 10000 * self.WEIGHTS[site_object.position]
                    else:
                        file.write(
                            f'Сайт: {site_object.content_object.domain}. Объем статьи {site_object.content_object.letters_amount}. Находится на {site_object.position}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {site_object.content_object.letters_amount * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                        real_concurency += site_object.content_object.letters_amount * self.WEIGHTS[
                            site_object.position]
                        max_concurency += 10000 * self.WEIGHTS[site_object.position]
                else:
                    file.write(
                        f'Сайт: {site_object.content_object.domain}. Контент не валиден (5000 знаков по умолчанию). Находится на {site_object.position}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {5000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                    real_concurency += 5000 * self.WEIGHTS[site_object.position]
                    max_concurency += 10000 * self.WEIGHTS[site_object.position]
            except:
                file.write(
                    f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {10000 * self.WEIGHTS[site_object.position]} из {10000 * self.WEIGHTS[site_object.position]}\n')
                real_concurency += 10000 * self.WEIGHTS[site_object.position]
                max_concurency += 10000 * self.WEIGHTS[site_object.position]
        file.write(
            f'Уровень конкуренции от объема контента: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_volume_concurency}\n')
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
                file.write(
                    f'Сайт: {site_object.content_object.domain}. Запрос: {self.request}. Стемированный тайтл: {site_object.content_object.stemmed_title}. Кол-во совпадений: {matched_stem_items}.Находится на {site_object.position} месте. Процент совпадений: {round(test, 2)}. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {test2} из максимальных {self.WEIGHTS[site_object.position]}.\n')
            else:
                file.write(
                    f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {self.WEIGHTS[site_object.position]} из {self.WEIGHTS[site_object.position]}\n')
                real_concurency += self.WEIGHTS[site_object.position]
        file.write(
            f'Уровень конкуренции от стема: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_stem_concurency}\n')
        file.write('----------------------------------------\n')
        file.write('Апскейл от директа:\n')

        direct_upscale = 0
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
                    real_concurency += site_object.domain_object.unique_backlinks * self.WEIGHTS[site_object.position]
                    file.write(
                        f'Сайт: {site_object.content_object.domain}. Количество бэклинков: {site_object.domain_object.unique_backlinks}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]} Сложность повысилась на {site_object.domain_object.unique_backlinks * self.WEIGHTS[site_object.position]} из {500 * self.WEIGHTS[site_object.position]}\n')
                else:
                    real_concurency += 500 * self.WEIGHTS[site_object.position]
                    file.write(
                        f'Сайт: {site_object.url}. Тип сайта: {site_object.site_type}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]}. Сложность повысилась на {500 * self.WEIGHTS[site_object.position]} из {500 * self.WEIGHTS[site_object.position]}\n')
            file.write(
                f'Уровень конкуренции от бэклинков: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_backlinks_concurency}\n')

            file.write(f'Итоговая конкуренция:\n')
            total_difficulty = int(
                self.site_age_concurency * self.importance['Возраст сайта'] + self.site_stem_concurency *
                self.importance[
                    'Стемирование'] + self.site_volume_concurency * self.importance[
                    'Объем статей'] + self.site_backlinks_concurency * self.importance['Ссылочное'])

            file.write(
                f"От возраста: {self.site_age_concurency} * {self.importance['Возраст сайта']} = {self.site_age_concurency * self.importance['Возраст сайта']}\n")
            file.write(
                f"От стема: {self.site_stem_concurency} * {self.importance['Стемирование']} = {self.site_stem_concurency * self.importance['Стемирование']}\n")
            file.write(
                f"От объема: {self.site_volume_concurency} * {self.importance['Объем статей']} = {self.site_volume_concurency * self.importance['Объем статей']}\n")
            file.write(
                f"От ссылочного: {self.site_backlinks_concurency} * {self.importance['Ссылочное']} = {self.site_backlinks_concurency * self.importance['Ссылочное']}\n")
            file.write(f'До вычета direct upscale: {total_difficulty}\n')

            total_difficulty += direct_upscale
            file.write(f'После вычета direct upscale ({direct_upscale}): {total_difficulty}\n')



        else:
            file.write('Бэклинков недостаточно\n')
        file.close()
        print('ya')

    def convert_vital_domains_to_sting(self):
        self.vital_domains_amount = len(self.vital_domains)
        self.vital_domains = ' '.join(self.vital_domains)


if __name__ == "__main__":
    while True:
        Manager()
        time.sleep(10)