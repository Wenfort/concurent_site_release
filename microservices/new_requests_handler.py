from microservices.conc_settings import *
from multiprocessing import Process, Queue
from threading import Thread
from loguru import logger
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from microservices import postgres_mode as pm
import re
from dataclasses import dataclass, field
from main.tools.stemmer import stem_text


@dataclass
class RequestDataSet:
    id: int
    text: str
    xml: str
    xml_status: str
    region_id: int


@dataclass
class SiteDataSet:
    html: str = ''
    type: str = ''
    order_on_page: int = 1

    domain: str = ''
    invalid_domain_zone: bool = False
    domain_age: int = 0
    unique_backlinks: int = 0
    total_backlinks: int = 0
    backlinks_status: str = ''
    domain_group: int = 0

    content_letters_amount: int = 0
    content_stemmed_title: list = field(default_factory=lambda: [])
    is_content_valid: bool = True


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

        database_return = pm.custom_request_to_database_with_return(sql)
        keys_list = [key[0] for key in database_return]
        return keys_list

    @staticmethod
    def _get_balance(key):
        url = f'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey={key}&host=yandex.ru&parameterList=spam'
        balance_request_return = requests.get(url).json()
        return balance_request_return['hostLimitsBalance']

    @staticmethod
    def _delete_checktrust_zero_balance_accounts(zero_balance_accounts_count):
        if zero_balance_accounts_count:
            sql = ('DELETE FROM concurent_site.main_payload '
                   'WHERE balance = 0;')

            pm.custom_request_to_database_without_return(sql)

    @staticmethod
    def _update_checktrust_api_balance_accounts(key, balance):
        sql = f"UPDATE concurent_site.main_payload SET balance = {balance} WHERE key = '{key}';"

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

class Site:
    def __init__(self, site_dataset):
        self.site_dataset = site_dataset

        self.url = str()
        self.html = str()

        self.get_url()
        self.get_site_type()
        self.get_domain()

        self.get_html()
        self.add_domain_data_to_dataset()
        self.add_content_data_to_dataset()

    def get_url(self):
        self.url = self.site_dataset.html.find('url').text
        if 'http' not in self.url:
            self.url = 'https://' + self.url

    def get_site_type(self):
        """
        Иногда, XML сервис работает некорректно и показывает полное отсутствие рекламных блоков. Но, на самом деле,
        они есть. Просто спарсились как стандартные объявления вида yabs.yandex.ru.
        Этот метод перепроверяет estimated_site_type и выносит окончательный вердикт, является ли сайт рекламный.
        Перепроверка по URL, а не по всему html блоку занимает не очень много времени,
        но делает результаты на 100% точными.
        """
        if self.site_dataset.type == 'direct' or 'yabs.yandex.ru' in self.url:
            self.site_dataset.type = 'direct'

    def get_domain(self):
        """
        Домены могут быть разных уровней. В большинстве случаев достаточно просто получить домен с помощью
        библиотеки urlparse и отрезать www. Но иногда, яндекс показывает домены без указания первого уровня. Напимер:
        okna-msk. К таким доменам автоматически добавляется .ru. В to-do листе есть задача по более точному
        определению домена первого уровня, так как, теориетически, это может быть и .net и .com, но пока не реализована.
        Еще одна проблема - домены третьего и даже четвертого уровня. Цикл проходит по таким доменам и обрезает лишнее
        вплоть до домена 2 уровня.
        Самый спорный момент - присвоение домена abstract-average-site.ru при нахождении Турбо Страницы. Так как
        реальный url можно получить только после открытия турбо-страницы, а они генерируются с помощью JS, необходимо
        поднимать Selenium. И поскольку Selenium в проекте больше нигде не используется, пришлось бы заложить
        дополнительные требования к ОЗУ, что приведет к удорожанию проекта. Либо можно просто
        пожертвовать незначительной долей точности и обрабатывать турбо страницы (они встречаются довольно редко) как
        абстрактный сайт с усредненными показателями
        """
        domain = urlparse(self.url)
        domain = domain.netloc
        domain = domain.replace('www.', '')

        if 'Турбо-страница' in domain:
            domain = 'abstract-average-site.ru'

        if domain.count('.') == 0:
            domain = domain + '.ru'

        while domain.count('.') != 1:
            first_dot = domain.find('.') + 1
            domain = domain[first_dot:]

        self.site_dataset.domain = domain

    def is_pdf(self):
        if '.pdf' in self.url:
            return True

    def get_html(self):
        """
        Метод принимает URL и перепроверяет не ведет ли он на pdf файл. Если все в порядке, то собирантся html под
        сайта и парсится с помощью BS4. Если сайт лежит или стоит защита от парсинга контента - возвращается пустой html
        такое случается редко, радикального влияние на точность результатов не оказывает
        """
        if not self.is_pdf():
            try:
                r = requests.get(self.url, headers=HEADERS, verify=False, timeout=15).content
                self.html = BeautifulSoup(r, 'html.parser')
            except:
                self.html = ''
                self.site_dataset.is_content_valid = False
        else:
            self.html = ''
            self.site_dataset.is_content_valid = False

    def add_domain_data_to_dataset(self):
        Domain(self.site_dataset)

    def add_content_data_to_dataset(self):
        Content(self.html, self.site_dataset)


class Yandex:
    def __init__(self, request_dataset, q):
        self.request_id = request_dataset.id
        self.request_text = request_dataset.text
        self.xml_text = request_dataset.xml
        self.region_id = request_dataset.region_id
        self.q = q

        self.site_list = list()
        self.thread_list = str()
        self.concurency_object = object()
        self.order_on_page = 1

        self.start_logging()
        self.stemmed_request = stem_text(self.request_text)
        self.parse_xml_text_with_bs4()
        self.get_request_views()
        self.get_site_list()

        self.clean_garbage()

        self.run_threads()

        self.make_concurency_object()
        self.prepare_result()
        self.add_result_to_database()
        self.change_request_status_in_queue()

        self.q.put('ready')

    def change_request_status_in_queue(self):
        """
        Если в процессе обхода были собраны не все бэклинки, то строке в таблице main_handledxml присваивается
        значение backlinks. Это нужно для повторного использования xml кода сервисом pending_request_handler.
        Иначе, присваивается статус confirmation, означающий, что по бэклинкам достаточно данных.
        Confirm означает, что решение об удалении запроса из очереди передается  микросервису
            xml_handler. Он удалит этот запрос из очереди после завершения всех перепроверок объявлений
            в очереди. Запросы без статуса confirm удалены не будут, так как их еще не обработал
            new_requests_handler.
        """
        if self.concurency_object.status == 'backlinks':
            sql = f"UPDATE concurent_site.main_handledxml SET status = 'pending' WHERE request_id = {self.request_id};"
            pm.custom_request_to_database_without_return(sql)
        else:
            sql = f"UPDATE concurent_site.main_handledxml SET status = 'confirm' WHERE request_id = {self.request_id};"
            pm.custom_request_to_database_without_return(sql)

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

    def parse_xml_text_with_bs4(self):
        self.xml_text = BeautifulSoup(self.xml_text, 'lxml')

    def _parse_url_data_from_page_xml(self, xml_tag, ad_tag=''):
        """
        Метод ищет в xml список сайтов внутри тега xml_tag. Очень важно разделить рекламные сайты и органические,
        поэтому в некоторых случаях передается необязательный аргумент ad_tag. Если в ad_tag нет сайтов, возвращается
        пустой список
        """
        if ad_tag:
            try:
                return self.xml_text.find(ad_tag).find_all(xml_tag)
            except:
                return []
        else:
            return self.xml_text.find_all(xml_tag)

    def _prepare_datasets(self, site_list, site_list_type):
        """
        Метод принимает распаршенный список html блоков. Каждый из блок - сниппет сайта из поисковой страницы Яндекса.
        Также, метод принимает тип списка: direct(реклама) или organic(не реклама)
        Подготавливается датасет, в который отправлется html блок из списка site_list, тип сайта и его
            порядок на поисковой странице Яндекса
        """
        for site in site_list:
            site_dataset = SiteDataSet(html=site, type=site_list_type, order_on_page=self.order_on_page)
            self.order_on_page += 1
            self.site_list.append(site_dataset)

    def _prepare_all_datasets(self, top_direct_sites, organic_sites, bottom_direct_sites):
        self._prepare_datasets(top_direct_sites, 'direct')
        self._prepare_datasets(organic_sites, 'organic')
        self._prepare_datasets(bottom_direct_sites, 'direct')

    def get_site_list(self):
        top_direct_sites = self._parse_url_data_from_page_xml('query', 'topads')
        organic_sites = self._parse_url_data_from_page_xml('doc')
        bottom_direct_sites = self._parse_url_data_from_page_xml('query', 'bottomads')

        self._prepare_all_datasets(top_direct_sites, organic_sites, bottom_direct_sites)

        logger.info(f'Собран список сайтов {self.request_text}')

    def clean_garbage(self):
        """
        Полный XML страницы больше не понадобится, при этом, он занимает очень много места в оперативной памяти.
        """
        del self.xml_text

    def make_site_object(self, site_dataset):
        Site(site_dataset)

    def run_threads(self):
        self.make_threads()
        self.start_threads()
        self.check_threads()

    def make_threads(self):
        self.thread_list = [Thread(target=self.make_site_object, args=(site_dataset,))
                            for site_dataset in self.site_list]

    def start_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def make_concurency_object(self):
        self.concurency_object = Concurency(self.site_list, self.stemmed_request)

    def prepare_result(self):
        self.result = self.concurency_object

    def add_result_to_database(self):
        if self.concurency_object.all_backlinks_collected:
            self.concurency_object.status = 'ready'
        else:
            self.concurency_object.status = 'backlinks'

        pm.custom_request_to_database_without_return(
            f"UPDATE concurent_site.main_request SET "
            f"age_concurency = {self.concurency_object.site_age_concurency}, "
            f"stem_concurency = {self.concurency_object.site_stem_concurency}, "
            f"volume_concurency = {self.concurency_object.site_volume_concurency}, "
            f"backlinks_concurency = {self.concurency_object.site_backlinks_concurency}, "
            f"total_concurency = {self.concurency_object.site_total_concurency}, "
            f"direct_upscale = {self.concurency_object.direct_upscale}, "
            f"status = '{self.concurency_object.status}', "
            f"direct_concurency = {self.concurency_object.site_direct_concurency}, "
            f"seo_concurency = {self.concurency_object.site_seo_concurency}, "
            f"views = {self.request_views}, "
            f"average_age = {self.concurency_object.average_site_age}, "
            f"average_volume = {self.concurency_object.average_site_volume}, "
            f"average_total_backlinks = {self.concurency_object.average_total_backlinks}, "
            f"average_unique_backlinks = {self.concurency_object.average_unique_backlinks} "
            f"WHERE id = {self.request_id}"
        )


class Backlinks:
    def __init__(self, site_dataset):
        self.site_dataset = site_dataset
        self.token = str()
        self.status = str()

        self.get_token()
        self.get_backlinks()

    def get_token(self):
        sql = "SELECT key FROM concurent_site.main_payload WHERE balance > 25 LIMIT 1;"

        answer_from_database = pm.custom_request_to_database_with_return(sql, 'one')
        self.token = answer_from_database[0]

    def _get_backlinks_service_json_answer(self, domain):
        service_api_url = 'https://checktrust.ru/app.php?r=host/app/summary/basic&applicationKey='
        params = 'parameterList=mjDin,mjHin'
        api_request_url = f'{service_api_url}{self.token}&host={domain}&{params}'

        request_json = requests.get(api_request_url).json()
        return request_json

    def get_backlinks(self):
        request_json = self._get_backlinks_service_json_answer(self.site_dataset.domain)
        print(f'Попробовали получить данные от домена {self.site_dataset.domain}')
        if not request_json['success']:
            logger.info(f'{self.site_dataset.domain} данные не получены по причине {request_json["message"]}')
            self.site_dataset.backlinks_status = 'pending'
        else:
            self.site_dataset.unique_backlinks = int(request_json["summary"]["mjDin"])
            self.site_dataset.total_backlinks = int(request_json["summary"]["mjHin"])
            self.site_dataset.backlinks_status = 'complete'

            if self.site_dataset.unique_backlinks >= 10000 or self.site_dataset.total_backlinks >= 30000:
                self.site_dataset.domain_group = 1


class Domain:
    def __init__(self, site_dataset):
        self.site_dataset = site_dataset
        self.domain_data_in_database = list()

        if self.is_domain_data_in_database():
            self.add_domain_data_to_dataset()
        else:
            try:
                self.get_domain_data()
            except:
                logger.critical(f'Проблемы с доменом {self.domain}')

    def get_domain_data(self):
        self.get_domain_age()
        self.add_backlinks_data_to_dataset()
        self.add_domain_backlinks_to_database()

    def add_domain_data_to_dataset(self):
        self.site_dataset.domain_age = self.domain_data_in_database[0]
        self.site_dataset.unique_backlinks = self.domain_data_in_database[1]
        self.site_dataset.total_backlinks = self.domain_data_in_database[2]
        self.site_dataset.domain_group = self.domain_data_in_database[3]
        self.site_dataset.backlinks_status = self.domain_data_in_database[4]

    def is_domain_data_in_database(self):
        sql = ("SELECT age, unique_backlinks, total_backlinks, domain_group, status "
               "FROM concurent_site.main_domain "
               f"WHERE "
               f"name = '{self.site_dataset.domain}';")

        self.domain_data_in_database = pm.custom_request_to_database_with_return(sql, 'one')

        if self.domain_data_in_database:
            return True

    def add_domain_backlinks_to_database(self):
        """
        Может сложиться так, что два процесса пытаются одновременно добавить один и тот же домен в БД.
        Для обработки этой коллизии используется исключение
        """
        sql = ("INSERT INTO "
               "concurent_site.main_domain(name, age, unique_backlinks, total_backlinks, status, domain_group) "
               "VALUES "
               f"('{self.site_dataset.domain}', {self.site_dataset.domain_age}, {self.site_dataset.unique_backlinks},"
               f"{self.site_dataset.total_backlinks}, '{self.site_dataset.backlinks_status}',"
               f"{self.site_dataset.domain_group});")

        try:
            pm.custom_request_to_database_without_return(sql)
        except Exception as e:
            print(e)


    def _get_domain_age_with_creation_date_pattern(self, soup):
        start = soup.find('Creation Date') + 15
        finish = start + 4
        year = soup[start:finish]
        self.site_dataset.domain_age = CURRENT_YEAR - int(year)

    def _get_domain_age_with_registered_on_pattern(self, soup):
        start = soup.find('Registered on')
        finish = soup.find('Registry fee')
        year = soup[start:finish].split()[4]
        self.site_dataset.domain_age = CURRENT_YEAR - int(year)

    def _get_domain_age_with_created_pattern(self, soup):
        """
        В отчетах по доменным зонам из кортежа invalid_domain_zones отсутствует год регистрации домена.
        Однако, в них присутствует слово 'created', которое используется для идентификации паттерна.
        Валидности данных о возрасте в таком случае присваивается флаг False, а возраст остается пустым.
        """
        invalid_domain_zones = ('.lv', '.club', '.to', '.ua', '.eu')
        if any(zone in self.site_dataset.domain for zone in invalid_domain_zones):
            self.site_dataset.invalid_domain_zone = False
        else:
            start = soup.find('created') + 8
            finish = start + 4
            item = soup[start:finish]
            self.site_dataset.domain_age = CURRENT_YEAR - int(item)

    def get_domain_age(self):
        """
        Чтобы получить возраст домена, необходимо обратиться к стороннему сервису, распарсить ответ и сравнить с
        номером текущего года.
        Сложность задачи в том, что во-первых, сторонний сервис поддерживает не все доменные зоны, а во-вторых,
        формат ответа у разных доменных зон отичается. Есть три основных паттерна, использующих слова:
        Creation Date
        Registered on
        created
        В зависимости от наличия этих слов в html, запускается соответствующий паттерн обработки данных.
        Если нашлась какая-то необычная доменная зона, домен добавляется в лог файл, валидность данных о возрасте в
        таком случае присваивается флаг False, а возраст остается пустым.
        """
        URL = f'https://www.nic.ru/whois/?searchWord={self.site_dataset.domain}'
        r = requests.get(URL).content
        soup = BeautifulSoup(r, 'html.parser').text

        try:
            if 'Creation Date' in soup:
                self._get_domain_age_with_creation_date_pattern(soup)
            elif 'Registered on' in soup:
                self._get_domain_age_with_registered_on_pattern(soup)
            elif 'created' in soup:
                self._get_domain_age_with_created_pattern(soup)
        except:
            logger.critical(f'Возраст домена {self.domain} определен неправильно')
            self.site_dataset.invalid_domain_zone = False

    def add_backlinks_data_to_dataset(self):
        Backlinks(self.site_dataset)


class Content:
    def __init__(self, html, site_dataset):
        self.site_dataset = site_dataset
        self.html = html

        self.text = str()

        if self.site_dataset.type == 'organic' and self.site_dataset.is_content_valid:
            try:
                self.get_text()
                self.add_letters_amount_to_dataset()
                self.add_stemmed_title_to_dataset()
            except:
                self.site_dataset.is_content_valid = False
                logger.critical(f"Проблема с валидностью контента {self.site_dataset.domain}. ")

    def add_stemmed_title_to_dataset(self):
        """
        Метод стеммирует тайтл и помещает его в датасет
        """
        title = self.get_title()
        title_without_puctuation = self.delete_punctuation_from_title(title)
        self.site_dataset.content_stemmed_title = stem_text(title_without_puctuation)

    def get_text(self):
        """
        Из html парсится текст и очищается от переносов.
        """
        self.text = self.html.text.replace('\n', '')

    def add_letters_amount_to_dataset(self):
        self.site_dataset.content_letters_amount = len(self.text)

    def get_title(self):
        title = self.html.find('title').text
        title = title.replace('\n', '')

        return title

    def delete_punctuation_from_title(self, title):
        title_without_puctuation = re.sub(r'[^\w\s]', '', title)
        return title_without_puctuation


class Concurency:
    def __init__(self, site_datasets, stemmed_request):
        self.site_datasets = site_datasets
        self.stemmed_request = stemmed_request

        self.WEIGHTS = dict()
        self.importance = dict()
        self.site_age_concurency = int()
        self.site_stem_concurency = int()
        self.site_volume_concurency = int()
        self.site_backlinks_concurency = int()
        self.site_total_concurency = int()
        self.site_seo_concurency = int()
        self.site_direct_concurency = int()
        self.direct_upscale = int()

        self.direct_sites_amount = int()
        self.organic_sites_amount = int()

        self.average_site_age = int()
        self.average_site_volume = int()
        self.average_unique_backlinks = int()
        self.average_total_backlinks = int()
        self.all_backlinks_collected = True

        self.get_stat_weights()
        self.get_params_importance()
        self.calculate_statistics()

        self.calculate_site_stem_concurency()
        self.calculate_site_age_concurency()
        self.calculate_site_volume_concurency()
        self.calculate_direct_upscale()
        self.calculate_direct_concurency()

        if self.all_backlinks_collected:
            self.calculate_site_backlinks_concurency()
            self.calculate_site_total_concurency()

    def get_params_importance(self):
        """
        IMPORTANCE - вес разных параметров конкуренции. В зависимости от абсурдности запроса, вес меняется.
        """
        if self._check_is_absourd_request():
            self.importance = ABSURD_IMPORTANCE
        else:
            self.importance = STANDART_IMPORTANCE

    def get_stat_weights(self):
        """
        WEIGHTS - вес разных позиций в поисковоый выдаче при оценке конкуренции.
        В зависимости от присутствия в выдаче директа, вес меняется.
        """
        if self._is_direct_in_dataset:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC

    def _is_direct_in_dataset(self):
        """
        Происходит проверка, есть ли в списке датасетов рекламные сайты. Для этого достаточно проверить первый
        и последний датасет. Реклама всегда находится либо в начале, либо в конце.
        """
        site_datasets_amount = len(self.site_datasets)
        first_dataset = self.site_datasets[0]
        last_dataset = self.site_datasets[site_datasets_amount - 1]
        if first_dataset.type == 'direct' or last_dataset.type == 'direct':
            return True

    def _calculate_concurency(self, max_important_value, attribute_name):
        max_concurency = 0
        real_concurency = 0

        for site_dataset in self.site_datasets:
            concurency_attribute = getattr(site_dataset, attribute_name)
            max_concurency += max_important_value * self.WEIGHTS[site_dataset.order_on_page]

            if site_dataset.type == 'direct' or concurency_attribute > max_important_value:
                real_concurency += max_important_value * self.WEIGHTS[site_dataset.order_on_page]
            else:
                real_concurency += concurency_attribute * self.WEIGHTS[site_dataset.order_on_page]

        concurency_percent = int(real_concurency / max_concurency * 100)

        return concurency_percent

    def calculate_site_age_concurency(self):
        """
        Метод обходит каждый датасет в списке датасетов.
        Создаются две переменные:
            max_age_concurency накапливает максимально возможную сложность по формуле: '10 * позиция сайта в поиске'
            real_age_concurency накапливает реальную сложность запроса по формуле
                'возраст сайта * позиция сайта в поиске'.
        Чтобы привести результаты к единообразию, максимальный возраст сайта ограничен 10-летием. Это важно, т.к.
            супер-витальные 25-летние сайты просто смазывали бы всю картину за счет своего возраста и резко бы завышали
            конкуренцию. Но так как в выдаче не 1 место, а 20, наличие в ней пары супер-витальных сайтов не так важно.
        Итоговая конкуренция считается по 100-балльной системе. Необходимо разделить реальную сложность на
        максимальную и умножить на 100.
        """

        self.site_age_concurency = self._calculate_concurency(10, 'domain_age')

    def calculate_site_volume_concurency(self):
        """
        Метод обходит каждый датасет в списке датасетов.
        Создаются две переменные:
            max_volume_concurency накапливает максимально возможную сложность по формуле:
                '10000 * позиция сайта в поиске'
            real_volume_concurency накапливает реальную сложность запроса по формуле:
                'количество знаков в контенте * позиция сайта в поиске'.
        Чтобы привести результаты к единообразию, максимальный объем контента сайта ограничен 10000 знаков.
            Это важно, т.к. супер-объемыные сайты просто смазывали бы всю картину за счет супер-лонгридов и резко бы
            завышали конкуренцию. Но так как в выдаче не 1 место, а 20, наличие в ней пары супер-витальных сайтов
            не так важно.
        Итоговая конкуренция считается по 100-балльной системе. Необходимо разделить реальную сложность на
        максимальную и умножить на 100.
        """
        self.site_volume_concurency = self._calculate_concurency(10000, 'content_letters_amount')

    def calculate_site_stem_concurency(self):
        """
        Метод обходит каждый датасет в списке датасетов.
        Создаются две переменные:
            max_stem_concurency накапливает максимально возможную сложность по формуле '1 * позиция сайта в поиске'
            real_stem_concurency накапливает реальную сложность запроса по формуле
                'matched_stem_items_amount (от 0 до 1) * позиция сайта в поиске'.
        Итоговая конкуренция считается по 100-балльной системе. Необходимо разделить реальную сложность на
        максимальную и умножить на 100.
        """
        max_stem_concurency = 0
        real_stem_concurency = 0

        for site_dataset in self.site_datasets:
            max_stem_concurency += self.WEIGHTS[site_dataset.order_on_page]
            if site_dataset.type == 'direct':
                real_stem_concurency += self.WEIGHTS[site_dataset.order_on_page]
            else:
                matched_stem_items_amount = self.count_matched_stem_items(site_dataset.content_stemmed_title)
                real_stem_concurency += matched_stem_items_amount / len(self.stemmed_request) * self.WEIGHTS[
                    site_dataset.order_on_page]

        self.site_stem_concurency = int(real_stem_concurency / max_stem_concurency * 100)

    def count_matched_stem_items(self, stemmed_title):
        """
        Возвращает количество совпадений в стемированном title и стемированном запросе пользователя.
        """
        matched_stemmed_words = set(stemmed_title) & set(self.stemmed_request)
        matched_stemmed_words_amount = len(matched_stemmed_words)

        return matched_stemmed_words_amount

    def _check_is_absourd_request(self):
        """
        Иногда, пользователи задают абсурдные запросы. Например "Купить слона в Нижневартовске с подъемом на этаж".
        Яндекс покажет максимально релевантные результаты. Например, мягкие игрушки или футболки с принтами.
        Однако, очевидно, что доставка слонов - другая ниша. Поэтому, если количество совпадений в тайтле сайтов
        и запросе пользователя не превышает 30%, запрос считается "абсурдным". 30% - не идеал, этот брейкпоинт
        тестируется.
        """
        if self.site_stem_concurency < 30:
            return True

    def calculate_statistics(self):
        """
        Метод обходит каждый датасет в списке датасетов.
        Цель обхода - собрать статистические данные из датасета: кол-во органик и директ сайтов, уникальные бэклинки,
        не уникальные бэклинки, количество знаков в контенте, возраст доменов.
        После этого вычисляет средние показатели.
        """
        unique_backlinks_total_count = 0
        total_backlinks_total_count = 0
        content_letters_total_count = 0
        domain_age_total_count = 0

        for site_dataset in self.site_datasets:
            if site_dataset.type == 'organic':
                self.organic_sites_amount += 1
                domain_age_total_count += site_dataset.domain_age
                content_letters_total_count += site_dataset.content_letters_amount

                if site_dataset.backlinks_status == 'complete' and self.all_backlinks_collected:
                    unique_backlinks_total_count += site_dataset.unique_backlinks
                    total_backlinks_total_count += site_dataset.total_backlinks
                else:
                    self.all_backlinks_collected = False
            else:
                self.direct_sites_amount += 1

        self.average_site_age = int(domain_age_total_count / self.organic_sites_amount)
        self.average_site_volume = int(content_letters_total_count / self.organic_sites_amount)

        if self.all_backlinks_collected:
            self.average_unique_backlinks = unique_backlinks_total_count / self.organic_sites_amount
            self.average_total_backlinks = total_backlinks_total_count / self.organic_sites_amount

    def calculate_site_backlinks_concurency(self):
        """
        Метод обходит каждый датасет в списке датасетов.
        Создаются две переменные:
            max_backlinks_concurency накапливает максимально возможную сложность по формуле:
                '500 * позиция сайта в поиске'
            real_backlinks_concurency накапливает реальную сложность запроса по формуле:
                'количество бэклинков * позиция сайта в поиске'.
        Чтобы привести результаты к единообразию, максимальное количество уник бэклинков сайта ограничен 500 ссылками.
            Это важно, т.к. супер-трастовые просто смазывали бы всю картину за счет огромного ссылочного
            профиля и резко бы завышали конкуренцию. Но так как в выдаче не 1 место, а 20, наличие в ней пары
            супер-витальных сайтов не так важно.
        Итоговая конкуренция считается по 100-балльной системе. Необходимо разделить реальную сложность на
        максимальную и умножить на 100.
        """

        self.site_backlinks_concurency = self._calculate_concurency(500, 'unique_backlinks')

    def calculate_direct_upscale(self):
        """
        direct_upscale - условные единицы повышения конкуренции по поисковому запросу из-за наличия рекламных блоков

        Метод подсчитывает количество объявлений в верхней и нижней части страницы поисковой выдачи.
        У каждого из объявлений разный коэффицент важности. Объявление на первом месте поисковой выдачи гораздо важнее,
            чем то, что находится под результатами поиска. И гораздо больше влияет на конкуренцию.
        В нижней части страницы могут находиться максимум 5 объявлений, в верхней - 4. В сумме - 9.
        """
        if self.direct_sites_amount >= 5:
            self.direct_upscale += 8
            self.direct_sites_amount -= 5

            if self.direct_sites_amount == 4:
                self.direct_upscale += 27
            elif self.direct_sites_amount == 3:
                self.direct_upscale += 23
            elif self.direct_sites_amount == 2:
                self.direct_upscale += 17
            elif self.direct_sites_amount == 1:
                self.direct_upscale += 8
        else:
            if self.direct_sites_amount == 5:
                self.direct_upscale += 8
            elif self.direct_sites_amount == 4:
                self.direct_upscale += 6.4
            elif self.direct_sites_amount == 3:
                self.direct_upscale += 4.8
            elif self.direct_sites_amount == 2:
                self.direct_upscale += 3.2
            elif self.direct_sites_amount == 1:
                self.direct_upscale += 1.6

    def _calculate_base_total_difficulty(self):
        """
        У каждого из факторов итоговой конкуренции есть собственная важность. Она находится в словаре self.importance.
        Базовая итоговая сложность конкуренции - результат сложения каждого из видов оценки конкуренции, умноженного
        на важность этих видов конкуренции.
        """
        age_share_in_total_concurency = self.site_age_concurency * self.importance['Возраст сайта']
        stem_share_in_total_concurency = self.site_stem_concurency * self.importance['Стемирование']
        volume_share_in_total_concurency = self.site_volume_concurency * self.importance['Объем статей']
        backlinks_share_in_total_concurency = self.site_backlinks_concurency * self.importance['Ссылочное']

        base_total_difficulty = age_share_in_total_concurency + stem_share_in_total_concurency + \
                                volume_share_in_total_concurency + backlinks_share_in_total_concurency

        return int(base_total_difficulty)

    def calculate_site_total_concurency(self):
        """
        Итоговая сложность конкуренции считается по формуле "базовая сложность" + "эффект повышения сложности от
        рекламных блоков (direct_upscale)
        """

        base_total_difficulty = self._calculate_base_total_difficulty()
        total_difficulty = base_total_difficulty + self.direct_upscale
        self.site_total_concurency = int(total_difficulty)

    def calculate_direct_concurency(self):
        """
        direct_concurency - рейтинг конкуренции, завязанный на процентгую шкалу. Считается с помощью деления
            накопленного direct upscale на 35 (максимально возможный upscale)
        """
        self.site_direct_concurency = int(self.direct_upscale / 35 * 100)


if __name__ == "__main__":
    while True:
        Manager()
        print('Готово!')
        time.sleep(10)
