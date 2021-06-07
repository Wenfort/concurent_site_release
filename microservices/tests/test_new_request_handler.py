import unittest
from microservices.new_requests_handler import Manager as NRHManager
from microservices.new_requests_handler import Yandex as NRHYandex
from microservices.new_requests_handler import Site as NRHSite
from microservices.new_requests_handler import Domain as NRHDomain
from microservices.new_requests_handler import Backlinks as NRHBacklinks
from microservices.new_requests_handler import Content as NRHContent
from microservices.new_requests_handler import Concurency as NRHConcurency
from microservices.new_requests_handler import RequestDataSet, SiteDataSet
from microservices import postgres_mode as pm
from main.tools.stemmer import stem_text
from bs4 import BeautifulSoup
from microservices.conc_settings import WEIGHTS_ORGANIC, WEIGHTS_DIRECT, STANDART_IMPORTANCE
import requests


class NRHUnitTestManager(NRHManager):
    def __init__(self):
        self.requests = list()


class NRHUnitTestYandex(NRHYandex):
    def __init__(self):
        pass


class NRHUnitTestSite(NRHSite):
    def __init__(self):
        pass


class NRHUnitTestDomain(NRHDomain):
    def __init__(self):
        pass


class NRHUnitTestBacklinks(NRHBacklinks):
    def __init__(self):
        pass


class NRHUnitTestContent(NRHContent):
    def __init__(self):
        pass


class NRHUnitTestConcurency(NRHConcurency):
    def __init__(self):
        pass

class TestManager(unittest.TestCase):

    def setUp(self):
        order_id = 1
        self.manager = TestManager()

        sql = ("INSERT INTO "
               "concurent_site.main_order "
               f"VALUES ({order_id}, 0, 0, 2, 1, 3) ")

        pm.custom_request_to_database_without_return(sql)

        sql = ("INSERT INTO "
               "concurent_site.main_request "
               f"VALUES "
               f"(1, 'Lasik', 0, 0, 0, 0, 0, 0, 0, 0, 'in work', 0, 0, 0, 0, 0, '', 0, 0, 255, {order_id}), "
               f"(2, 'Коррекция зрения', 0, 0, 0, 0, 0, 0, 0, 0, 'in work', 0, 0, 0, 0, 0, '', 0, 0, 255, {order_id})")

        pm.custom_request_to_database_without_return(sql)

        file = open("text_files_for_tests/first_xml_answer", "r")
        xml = file.read()
        file.close()

        sql = ("INSERT INTO "
               "concurent_site.main_requestqueue "
               f"VALUES (DEFAULT, FALSE, 255, 1)")

        pm.custom_request_to_database_without_return(sql)

        sql = ("INSERT INTO "
               "concurent_site.main_handledxml "
               f"VALUES "
               f"(DEFAULT, '{xml}', 'in work', 0, 0, 0, 0, 255, 1),"
               f"(DEFAULT, '{xml}', 'in work', 0, 0, 0, 0, 255, 2)")

        pm.custom_request_to_database_without_return(sql)

        file = open("text_files_for_tests/second_xml_answer", "r")
        xml = file.read()
        file.close()

        sql = ("INSERT INTO "
               "concurent_site.main_requestqueue "
               f"VALUES (DEFAULT, FALSE, 255, 2)")

        pm.custom_request_to_database_without_return(sql)

        sql = ("INSERT INTO "
               "concurent_site.main_domain "
               "VALUES "
               "('test-domain-one.ru', 8, 400, 800, 'complete', 0),"
               "('test-domain-two.ru', 12, 600, 1200, 'pending', 1),"
               "('test-domain-three.ru', 45, 100500, 1000000, 'fake', 2)")

        pm.custom_request_to_database_without_return(sql)

    def tearDown(self):
        SCHEMA = 'concurent_site'
        test_domains = ('test-domain-one.ru', 'test-domain-two.ru', 'test-domain-three.ru')
        sql = (f'DELETE FROM {SCHEMA}.main_order; '
               f'DELETE FROM {SCHEMA}.main_handledxml; '
               f'DELETE FROM {SCHEMA}.main_requestqueue; '
               f'DELETE FROM {SCHEMA}.main_request; '
               f'DELETE FROM {SCHEMA}.main_domain WHERE name in {test_domains};')

        pm.custom_request_to_database_without_return(sql)

    def test_setup_insertion_main_order(self):
        sql = "SELECT id FROM concurent_site.main_order;"
        database_return = pm.custom_request_to_database_with_return(sql, 'one')
        id = database_return[0]

        self.assertEqual(id, 1)

    def test_setup_insertion_main_request(self):
        sql = "SELECT id, text FROM concurent_site.main_request;"
        database_return = pm.custom_request_to_database_with_return(sql)

        first_request = database_return[0]
        second_request = database_return[1]

        self.assertEqual(first_request[0], 1)
        self.assertEqual(first_request[1], 'Lasik')
        self.assertEqual(second_request[0], 2)
        self.assertEqual(second_request[1], 'Коррекция зрения')

    def test_setup_insertion_main_requestqueue(self):
        sql = "SELECT request_id FROM concurent_site.main_requestqueue;"
        database_return = pm.custom_request_to_database_with_return(sql)

        first_request = database_return[0]
        second_request = database_return[1]

        self.assertEqual(first_request[0], 1)
        self.assertEqual(second_request[0], 2)

    def test_setup_insertion_main_handledxml(self):
        sql = "SELECT request_id FROM concurent_site.main_handledxml;"
        database_return = pm.custom_request_to_database_with_return(sql)

        first_request = database_return[0]
        second_request = database_return[1]

        self.assertEqual(first_request[0], 1)
        self.assertEqual(second_request[0], 2)

    def test_get_requests_from_queue(self):
        manager_object = NRHUnitTestManager()
        manager_object.get_requests_from_queue()

        request = manager_object.requests[0]
        self.assertEqual(1, request.id)
        self.assertEqual('Lasik', request.text)

        request = manager_object.requests[1]
        self.assertEqual(2, request.id)
        self.assertEqual('Коррекция зрения', request.text)

    def test_request_dataset_creation(self):
        file = open("text_files_for_tests/first_xml_answer", "r")
        xml = file.read()
        file.close()

        request_dataset = RequestDataSet(id=1, text='Lasik', xml=xml, xml_status='in work', region_id=255)

        self.assertEqual(request_dataset.id, 1)
        self.assertEqual(request_dataset.xml_status, 'in work')

    def test_stem_text(self):
        file = open("text_files_for_tests/second_xml_answer", "r")
        xml = file.read()
        file.close()

        request_dataset = RequestDataSet(id=2, text='Коррекция зрения', xml=xml, xml_status='in work', region_id=255)

        yandex_object = NRHUnitTestYandex()
        yandex_object.request_text = request_dataset.text
        stemmed_request = stem_text(yandex_object.request_text)
        self.assertEqual(stemmed_request, ['коррекция', 'зрение'])

    def test_parse_xml_text_with_bs4(self):
        file = open("text_files_for_tests/second_xml_answer", "r")
        xml = file.read()
        file.close()

        request_dataset = RequestDataSet(id=2, text='Коррекция зрения', xml=xml, xml_status='in work', region_id=255)

        yandex_object = NRHUnitTestYandex()
        yandex_object.xml_text = request_dataset.xml
        yandex_object.parse_xml_text_with_bs4()
        advcount = yandex_object.xml_text.find('advcount').text

        self.assertEqual(advcount, '4')

    def test_get_site_list(self):
        file = open("text_files_for_tests/second_xml_answer", "r")
        xml = file.read()
        file.close()

        request_dataset = RequestDataSet(id=2, text='Коррекция зрения', xml=xml, xml_status='in work', region_id=255)

        yandex_object = NRHUnitTestYandex()
        yandex_object.request_text = request_dataset.text
        yandex_object.xml_text = request_dataset.xml
        yandex_object.order_on_page = 1
        yandex_object.site_list = []

        yandex_object.parse_xml_text_with_bs4()
        yandex_object.get_site_list()

        first_dataset = yandex_object.site_list[0]
        second_dataset = yandex_object.site_list[4]

        self.assertEqual(first_dataset.order_on_page, 1)
        self.assertEqual(first_dataset.type, 'direct')
        self.assertEqual(second_dataset.order_on_page, 5)
        self.assertEqual(second_dataset.type, 'organic')

    def test_get_url(self):
        file = open("text_files_for_tests/yandex_block_html", "r")
        html = file.read()
        file.close()
        html = BeautifulSoup(html, 'html.parser')

        site_dataset = SiteDataSet(html=html, type='organic', order_on_page=5)
        site_object = NRHUnitTestSite()
        site_object.url = ''
        site_object.site_dataset = site_dataset

        site_object.get_url()
        self.assertEqual(site_object.url, 'https://lazernaya-korrekciya-zreniya.ru/')

    def test_get_site_type(self):
        first_site_dataset = SiteDataSet(type='organic', order_on_page=5)
        first_site_object = NRHUnitTestSite()
        first_site_object.url = 'https://lazernaya-korrekciya-zreniya.ru/'
        first_site_object.site_dataset = first_site_dataset
        first_site_object.get_site_type()

        second_site_dataset = SiteDataSet(type='organic', order_on_page=5)
        second_site_object = NRHUnitTestSite()
        second_site_object.url = 'yabs.yandex.ru'
        second_site_object.site_dataset = second_site_dataset
        second_site_object.get_site_type()

        self.assertEqual('organic', first_site_object.site_dataset.type)
        self.assertEqual('direct', second_site_object.site_dataset.type)

    def test_get_domain(self):
        site_urls = ('https://lazernaya-korrekciya-zreniya.ru/', 'Турбо-страница', 'world',
                     'hello.mello.my.wonderful.beautiful.world.ru', 'мой-магазин.рф', 'www.market.yandex.ru',
                     'www.ru')

        assert_pair = ('lazernaya-korrekciya-zreniya.ru', 'abstract-average-site.ru', 'world.ru', 'world.ru',
                       'мой-магазин.рф', 'yandex.ru', 'www.ru')
        site_dataset = SiteDataSet(type='organic', order_on_page=5)
        pair_number = 0
        for site_url in site_urls:
            site_object = NRHUnitTestSite()
            site_object.site_dataset = site_dataset
            site_object.url = site_url
            site_object.get_domain()
            self.assertEqual(assert_pair[pair_number], site_object.site_dataset.domain)

            pair_number += 1

    """
    def test_internet_connection(self):
        first_request = requests.get('https://ya.ru')
        second_request = requests.get('https://google.com')
        self.assertEqual(200, first_request.status_code)
        self.assertEqual(200, second_request.status_code)

    def test_get_html(self):
        site_dataset = SiteDataSet(is_content_valid=True)

        first_site_object = NRHUnitTestSite()
        first_site_object.html = ''
        first_site_object.site_dataset = site_dataset
        first_site_object.url = 'https://ya.ru'
        first_site_object.get_html()
        got_first_site_html = bool(first_site_object.html)

        second_site_object = NRHUnitTestSite()
        second_site_object.html = ''
        second_site_object.site_dataset = site_dataset
        second_site_object.url = 'https://jgfdgjfjiogjsdijgosd'
        second_site_object.get_html()
        got_second_site_html = bool(second_site_object.html)
        
        self.assertEqual(True, got_first_site_html)
        self.assertEqual(False, got_second_site_html)

    def test_get_domain_age(self):
        domains_list = ['yandex.ru', 'yahoo.com', 'riga.lv', 'highreighoifdgoidfhgdfonifew.ru']
        assertions_list = ((24, False), (26, False), (5, True), (5, True))
        pair_number = 0
        for domain in domains_list:

            dataset = SiteDataSet()
            domain_object = NRHUnitTestDomain()
            domain_object.site_dataset = dataset
            domain_object.site_dataset.domain = domain
            domain_object.get_domain_age()
            assertion_domain_age = assertions_list[pair_number][0]
            assertion_invalid_domain_zone = assertions_list[pair_number][1]
            self.assertEqual(assertion_domain_age, domain_object.site_dataset.domain_age)
            self.assertEqual(assertion_invalid_domain_zone, domain_object.site_dataset.invalid_domain_zone)

            pair_number += 1
    
    def test_get_backlinks(self):
        backlinks_object = NRHUnitTestBacklinks()
        backlinks_object.token = ''
        backlinks_object.get_token()
        backlinks_object.site_dataset = SiteDataSet(domain='yandex.ru')
        backlinks_object.get_backlinks()

        self.assertGreater(backlinks_object.site_dataset.unique_backlinks, 590000)
        self.assertGreater(backlinks_object.site_dataset.total_backlinks, 1000000000)
        self.assertEqual(1, backlinks_object.site_dataset.domain_group)
    
    """

    def test_is_pdf(self):
        first_site_object = NRHUnitTestSite()
        first_site_object.url = 'https://www.site.ru/document.pdf'

        second_site_object = NRHUnitTestSite()
        second_site_object.url = 'https://www.pdfo.ru/ordinar_page'

        third_site_object = NRHUnitTestSite()
        third_site_object.url = 'https://yandef.pd'

        self.assertEqual(True, first_site_object.is_pdf())
        self.assertEqual(None, second_site_object.is_pdf())
        self.assertEqual(None, third_site_object.is_pdf())

    def test_domain_data_in_database(self):
        dataset = SiteDataSet()

        first_domain_object = NRHUnitTestDomain()
        first_domain_object.site_dataset = dataset
        first_domain_object.domain_data_in_database = ''
        first_domain_object.site_dataset.domain = 'test-domain-one.ru'
        first_result = first_domain_object.is_domain_data_in_database()

        dataset = SiteDataSet()
        second_domain_object = NRHUnitTestDomain()
        second_domain_object.site_dataset = dataset
        second_domain_object.domain_data_in_database = ''
        second_domain_object.site_dataset.domain = 'fake-test-domain-one.ru'
        second_result = second_domain_object.is_domain_data_in_database()

        self.assertEqual(True, first_result)
        self.assertEqual(None, second_result)

    def test_add_domain_data_to_dataset(self):
        dataset = SiteDataSet()
        site_data = (8, 400, 800, 0, 'complete')

        domain_object = NRHUnitTestDomain()
        domain_object.site_dataset = dataset
        domain_object.domain_data_in_database = site_data
        domain_object.add_domain_data_to_dataset()

        self.assertEqual(8, domain_object.site_dataset.domain_age)
        self.assertEqual(400, domain_object.site_dataset.unique_backlinks)
        self.assertEqual(800, domain_object.site_dataset.total_backlinks)
        self.assertEqual(0, domain_object.site_dataset.domain_group)
        self.assertEqual('complete', domain_object.site_dataset.backlinks_status)

    def test_add_letters_amount_to_dataset(self):
        file = open("text_files_for_tests/site_html", "r")
        html = file.read()
        file.close()
        html = BeautifulSoup(html, 'html.parser')

        content_object = NRHUnitTestContent()
        content_object.site_dataset = SiteDataSet()
        content_object.html = html
        content_object.get_text()
        content_object.add_letters_amount_to_dataset()
        self.assertEqual(4607, content_object.site_dataset.content_letters_amount)

    def test_get_title(self):
        file = open("text_files_for_tests/site_html", "r")
        html = file.read()
        file.close()
        html = BeautifulSoup(html, 'html.parser')

        content_object = NRHUnitTestContent()
        content_object.site_dataset = SiteDataSet()
        content_object.html = html
        title = content_object.get_title()
        self.assertEqual('Яндекс', title)

    def test_delete_punctuation_from_title(self):
        first_title = 'Hello,!@#$%^&*()+|/":;,<>. World'
        second_title = 'Good day'

        content_object = NRHUnitTestContent()
        first_title_without_puctutation = content_object.delete_punctuation_from_title(first_title)
        second_title_without_puctutation = content_object.delete_punctuation_from_title(second_title)
        self.assertEqual('Hello World', first_title_without_puctutation)
        self.assertEqual('Good day', second_title_without_puctutation)

    def test_is_direct_in_datasets(self):
        first_datasets = (SiteDataSet(type='direct'), SiteDataSet(type='organic'), SiteDataSet(type='direct'))
        second_datasets = (SiteDataSet(type='direct'), SiteDataSet(type='organic'), SiteDataSet(type='organic'))
        third_datasets = (SiteDataSet(type='organic'), SiteDataSet(type='direct'), SiteDataSet(type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = first_datasets
        direct_in_datasets = concurency_object.check_is_direct_in_datasets()
        self.assertEqual(True, direct_in_datasets)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = second_datasets
        direct_in_datasets = concurency_object.check_is_direct_in_datasets()
        self.assertEqual(True, direct_in_datasets)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = third_datasets
        direct_in_datasets = concurency_object.check_is_direct_in_datasets()
        self.assertEqual(None, direct_in_datasets)

    def test_get_stats_weight(self):
        first_datasets = (SiteDataSet(type='direct'), SiteDataSet(type='organic'), SiteDataSet(type='direct'))
        second_datasets = (SiteDataSet(type='direct'), SiteDataSet(type='organic'), SiteDataSet(type='organic'))
        third_datasets = (SiteDataSet(type='organic'), SiteDataSet(type='direct'), SiteDataSet(type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = first_datasets
        concurency_object.WEIGHTS = ''
        concurency_object.get_stat_weights()
        self.assertEqual(15, concurency_object.WEIGHTS[2])

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = second_datasets
        concurency_object.WEIGHTS = ''
        concurency_object.get_stat_weights()
        self.assertEqual(15, concurency_object.WEIGHTS[2])

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = third_datasets
        concurency_object.WEIGHTS = ''
        concurency_object.get_stat_weights()
        self.assertEqual(22, concurency_object.WEIGHTS[2])

    def test_check_is_absourd_request(self):
        concurency_object = NRHUnitTestConcurency()

        concurency_object.site_stem_concurency = 50
        is_absourd_request = concurency_object._check_is_absourd_request()
        self.assertEqual(None, is_absourd_request)

        concurency_object.site_stem_concurency = 15
        is_absourd_request = concurency_object._check_is_absourd_request()
        self.assertEqual(True, is_absourd_request)

    def test_get_params_importance(self):
        concurency_object = NRHUnitTestConcurency()

        concurency_object.site_stem_concurency = 50
        concurency_object.importance = ''
        concurency_object.get_params_importance()
        self.assertEqual(0.4, concurency_object.importance['Возраст сайта'])
        self.assertEqual(0.2, concurency_object.importance['Ссылочное'])

        concurency_object.site_stem_concurency = 15
        concurency_object.importance = ''
        concurency_object.get_params_importance()
        self.assertEqual(0.15, concurency_object.importance['Возраст сайта'])
        self.assertEqual(0.15, concurency_object.importance['Ссылочное'])

    def test_calculate_statistics(self):
        first_datasets = (SiteDataSet(type='direct', domain_age=5, content_letters_amount=1000,
                                      backlinks_status='pending', unique_backlinks=500, total_backlinks=1000),
                          SiteDataSet(type='organic', domain_age=6, content_letters_amount=7000,
                                      backlinks_status='complete', unique_backlinks=900, total_backlinks=1200),
                          SiteDataSet(type='direct', domain_age=8, content_letters_amount=4200,
                                      backlinks_status='complete', unique_backlinks=300, total_backlinks=640))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.organic_sites_amount = int()
        concurency_object.site_datasets = first_datasets
        concurency_object.all_backlinks_collected = True
        concurency_object.direct_sites_amount = int()
        concurency_object.average_site_age = int()
        concurency_object.average_site_volume = int()
        concurency_object.average_unique_backlinks = int()
        concurency_object.average_total_backlinks = int()
        concurency_object.calculate_statistics()
        self.assertEqual(6, concurency_object.average_site_age)
        self.assertEqual(1, concurency_object.organic_sites_amount)
        self.assertEqual(2, concurency_object.direct_sites_amount)
        self.assertEqual(7000, concurency_object.average_site_volume)
        self.assertEqual(900, concurency_object.average_unique_backlinks)
        self.assertEqual(1200, concurency_object.average_total_backlinks)
        self.assertEqual(True, concurency_object.all_backlinks_collected)

        second_datasets = (SiteDataSet(type='direct', domain_age=5, content_letters_amount=1000,
                                      backlinks_status='pending', unique_backlinks=500, total_backlinks=1000),
                           SiteDataSet(type='organic', domain_age=6, content_letters_amount=7000,
                                      backlinks_status='complete', unique_backlinks=900, total_backlinks=1200),
                           SiteDataSet(type='organic', domain_age=8, content_letters_amount=4200,
                                      backlinks_status='complete', unique_backlinks=300, total_backlinks=640))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.organic_sites_amount = int()
        concurency_object.site_datasets = second_datasets
        concurency_object.all_backlinks_collected = True
        concurency_object.direct_sites_amount = int()
        concurency_object.average_site_age = int()
        concurency_object.average_site_volume = int()
        concurency_object.average_unique_backlinks = int()
        concurency_object.average_total_backlinks = int()
        concurency_object.calculate_statistics()
        self.assertEqual(7, concurency_object.average_site_age)
        self.assertEqual(2, concurency_object.organic_sites_amount)
        self.assertEqual(1, concurency_object.direct_sites_amount)
        self.assertEqual(5600, concurency_object.average_site_volume)
        self.assertEqual(600, concurency_object.average_unique_backlinks)
        self.assertEqual(920, concurency_object.average_total_backlinks)
        self.assertEqual(True, concurency_object.all_backlinks_collected)

        third_datasets = (SiteDataSet(type='organic', domain_age=5, content_letters_amount=1000,
                                      backlinks_status='pending', unique_backlinks=500, total_backlinks=1000),
                          SiteDataSet(type='direct', domain_age=6, content_letters_amount=7000,
                                      backlinks_status='complete', unique_backlinks=900, total_backlinks=1200),
                          SiteDataSet(type='organic', domain_age=8, content_letters_amount=4200,
                                      backlinks_status='complete', unique_backlinks=300, total_backlinks=640))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.organic_sites_amount = int()
        concurency_object.site_datasets = third_datasets
        concurency_object.all_backlinks_collected = True
        concurency_object.direct_sites_amount = int()
        concurency_object.average_site_age = int()
        concurency_object.average_site_volume = int()
        concurency_object.average_unique_backlinks = int()
        concurency_object.average_total_backlinks = int()
        concurency_object.calculate_statistics()
        self.assertEqual(6, concurency_object.average_site_age)
        self.assertEqual(2, concurency_object.organic_sites_amount)
        self.assertEqual(1, concurency_object.direct_sites_amount)
        self.assertEqual(2600, concurency_object.average_site_volume)
        self.assertEqual(0, concurency_object.average_unique_backlinks)
        self.assertEqual(0, concurency_object.average_total_backlinks)
        self.assertEqual(False, concurency_object.all_backlinks_collected)

    def test_count_matched_stem_items(self):
        concurency_object = NRHUnitTestConcurency()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        stemmed_title = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        matched_stem_words = concurency_object.count_matched_stem_items(stemmed_title)
        self.assertEqual(5, matched_stem_words)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        stemmed_title = ['слово', 'два', 'красивый', 'необычно', 'пятое']
        matched_stem_words = concurency_object.count_matched_stem_items(stemmed_title)
        self.assertEqual(3, matched_stem_words)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        stemmed_title = ['слово', 'один', 'красив', 'обычно', 'пятое']
        matched_stem_words = concurency_object.count_matched_stem_items(stemmed_title)
        self.assertEqual(4, matched_stem_words)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        stemmed_title = []
        matched_stem_words = concurency_object.count_matched_stem_items(stemmed_title)
        self.assertEqual(0, matched_stem_words)

    def test_calculate_site_stem_concurency(self):

        datasets = (SiteDataSet(content_stemmed_title=['слово', 'один', 'красивый', 'обычно', 'пятое'],
                                order_on_page=1, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'два', 'красивый', 'необычно', 'пятое'],
                                order_on_page=2, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'один', 'красив', 'обычно', 'пятое'],
                                order_on_page=3, type='organic'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(71, concurency_object.site_stem_concurency)

        datasets = (SiteDataSet(content_stemmed_title=['слово', 'один', 'красивый', 'обычно', 'пятое'],
                                order_on_page=1, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'два', 'красивый', 'необычно', 'пятое'],
                                order_on_page=2, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'один', 'красив', 'обычно', 'пятое'],
                                order_on_page=3, type='direct'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(74, concurency_object.site_stem_concurency)

        datasets = (SiteDataSet(content_stemmed_title=['слово', 'один', 'красивый', 'обычно', 'пятое'],
                                order_on_page=1, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'два', 'красивый', 'необычно', 'пятое'],
                                order_on_page=2, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'один', 'красив', 'обычно', 'пятое'],
                                order_on_page=3, type='organic'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(71, concurency_object.site_stem_concurency)

        datasets = (SiteDataSet(content_stemmed_title=['слово', 'один', 'красивый', 'обычно', 'пятое'],
                                order_on_page=1, type='organic'),
                    SiteDataSet(content_stemmed_title=['слово', 'два', 'красивый', 'необычно', 'пятое'],
                                order_on_page=2, type='direct'),
                    SiteDataSet(content_stemmed_title=['слово', 'один', 'красив', 'обычно', 'пятое'],
                                order_on_page=3, type='direct'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='direct'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(100, concurency_object.site_stem_concurency)

        datasets = (SiteDataSet(content_stemmed_title=['слово', 'один', 'красивый', 'обычно', 'пятое'],
                                order_on_page=1, type='direct'),
                    SiteDataSet(content_stemmed_title=['слово', 'два', 'красивый', 'необычно', 'пятое'],
                                order_on_page=2, type='direct'),
                    SiteDataSet(content_stemmed_title=['слово', 'один', 'красив', 'обычно', 'пятое'],
                                order_on_page=3, type='direct'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='direct'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(100, concurency_object.site_stem_concurency)

        datasets = (SiteDataSet(content_stemmed_title=[],
                                order_on_page=1, type='organic'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=2, type='organic'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=3, type='organic'),
                    SiteDataSet(content_stemmed_title=[],
                                order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_stem_concurency = int()
        concurency_object.stemmed_request = ['слово', 'один', 'красивый', 'обычно', 'пятое']
        concurency_object.calculate_site_stem_concurency()
        self.assertEqual(0, concurency_object.site_stem_concurency)

    def test_calculate_concurency(self):
        datasets = (SiteDataSet(domain_age=10, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_percent = concurency_object._calculate_concurency(10, 'domain_age')
        self.assertEqual(100, concurency_percent)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_percent = concurency_object._calculate_concurency(10, 'domain_age')
        self.assertEqual(60, concurency_percent)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='direct'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_age_concurency = int()
        concurency_percent = concurency_object._calculate_concurency(10, 'domain_age')
        self.assertEqual(100, concurency_percent)

    def test_calculate_site_age_concurency(self):
        datasets = (SiteDataSet(domain_age=10, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(100, concurency_object.site_age_concurency)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(60, concurency_object.site_age_concurency)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='direct'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(100, concurency_object.site_age_concurency)

    def test_calculate_site_backlinks_concurency(self):
        datasets = (SiteDataSet(unique_backlinks=500, order_on_page=1, type='organic'),
                    SiteDataSet(unique_backlinks=500, order_on_page=2, type='organic'),
                    SiteDataSet(unique_backlinks=2500, order_on_page=3, type='organic'),
                    SiteDataSet(unique_backlinks=3000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_backlinks_concurency = int()
        concurency_object.calculate_site_backlinks_concurency()
        self.assertEqual(100, concurency_object.site_backlinks_concurency)

        datasets = (SiteDataSet(unique_backlinks=0, order_on_page=1, type='organic'),
                    SiteDataSet(unique_backlinks=500, order_on_page=2, type='organic'),
                    SiteDataSet(unique_backlinks=2500, order_on_page=3, type='organic'),
                    SiteDataSet(unique_backlinks=3000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_backlinks_concurency = int()
        concurency_object.calculate_site_backlinks_concurency()
        self.assertEqual(60, concurency_object.site_backlinks_concurency)

        datasets = (SiteDataSet(unique_backlinks=0, order_on_page=1, type='direct'),
                    SiteDataSet(unique_backlinks=1000, order_on_page=2, type='organic'),
                    SiteDataSet(unique_backlinks=2500, order_on_page=3, type='organic'),
                    SiteDataSet(unique_backlinks=3000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_backlinks_concurency = int()
        concurency_object.calculate_site_backlinks_concurency()
        self.assertEqual(100, concurency_object.site_backlinks_concurency)

    def test_calculate_site_volume_concurency(self):
        datasets = (SiteDataSet(content_letters_amount=10000, order_on_page=1, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(100, concurency_object.site_volume_concurency)

        datasets = (SiteDataSet(content_letters_amount=0, order_on_page=1, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=25000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=30000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(60, concurency_object.site_volume_concurency)

        datasets = (SiteDataSet(content_letters_amount=0, order_on_page=1, type='direct'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=25000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=30000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(100, concurency_object.site_volume_concurency)

    def test_calculate_site_age_concurency(self):
        datasets = (SiteDataSet(domain_age=10, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(100, concurency_object.site_age_concurency)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='organic'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(60, concurency_object.site_age_concurency)

        datasets = (SiteDataSet(domain_age=0, order_on_page=1, type='direct'),
                    SiteDataSet(domain_age=10, order_on_page=2, type='organic'),
                    SiteDataSet(domain_age=25, order_on_page=3, type='organic'),
                    SiteDataSet(domain_age=30, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_age_concurency = int()
        concurency_object.calculate_site_age_concurency()
        self.assertEqual(100, concurency_object.site_age_concurency)

    def test_calculate_site_volume_concurency(self):
        datasets = (SiteDataSet(content_letters_amount=10000, order_on_page=1, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(100, concurency_object.site_volume_concurency)

        datasets = (SiteDataSet(content_letters_amount=0, order_on_page=1, type='organic'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=25000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=30000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_ORGANIC
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(60, concurency_object.site_volume_concurency)

        datasets = (SiteDataSet(content_letters_amount=0, order_on_page=1, type='direct'),
                    SiteDataSet(content_letters_amount=10000, order_on_page=2, type='organic'),
                    SiteDataSet(content_letters_amount=25000, order_on_page=3, type='organic'),
                    SiteDataSet(content_letters_amount=30000, order_on_page=4, type='organic'))

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_datasets = datasets
        concurency_object.WEIGHTS = WEIGHTS_DIRECT
        concurency_object.site_volume_concurency = int()
        concurency_object.calculate_site_volume_concurency()
        self.assertEqual(100, concurency_object.site_volume_concurency)

    def test_calculate_direct_upscale(self):
        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 0
        concurency_object.calculate_direct_upscale()
        self.assertEqual(0, concurency_object.direct_upscale)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 4
        concurency_object.calculate_direct_upscale()
        self.assertEqual(6.4, concurency_object.direct_upscale)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 5
        concurency_object.calculate_direct_upscale()
        self.assertEqual(8, concurency_object.direct_upscale)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 7
        concurency_object.calculate_direct_upscale()
        self.assertEqual(25, concurency_object.direct_upscale)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 8
        concurency_object.calculate_direct_upscale()
        self.assertEqual(31, concurency_object.direct_upscale)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.direct_upscale = int()
        concurency_object.direct_sites_amount = 9
        concurency_object.calculate_direct_upscale()
        self.assertEqual(35, concurency_object.direct_upscale)

    def test_calculate_direct_concurency(self):
        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_direct_concurency = int()
        concurency_object.direct_upscale = 35
        concurency_object.calculate_direct_concurency()
        self.assertEqual(100, concurency_object.site_direct_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_direct_concurency = int()
        concurency_object.direct_upscale = 17.5
        concurency_object.calculate_direct_concurency()
        self.assertEqual(50, concurency_object.site_direct_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_direct_concurency = int()
        concurency_object.direct_upscale = 0
        concurency_object.calculate_direct_concurency()
        self.assertEqual(0, concurency_object.site_direct_concurency)

    def test_calculate_base_total_difficulty(self):
        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_age_concurency = 100
        concurency_object.site_stem_concurency = 100
        concurency_object.site_volume_concurency = 100
        concurency_object.site_backlinks_concurency = 100
        concurency_object.importance = STANDART_IMPORTANCE
        base_total_concurency = concurency_object._calculate_base_total_difficulty()
        self.assertEqual(100, base_total_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_age_concurency = 100
        concurency_object.site_stem_concurency = 0
        concurency_object.site_volume_concurency = 100
        concurency_object.site_backlinks_concurency = 100
        concurency_object.importance = STANDART_IMPORTANCE
        base_total_concurency = concurency_object._calculate_base_total_difficulty()
        self.assertEqual(70, base_total_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_age_concurency = 100
        concurency_object.site_stem_concurency = 50
        concurency_object.site_volume_concurency = 100
        concurency_object.site_backlinks_concurency = 100
        concurency_object.importance = STANDART_IMPORTANCE
        base_total_concurency = concurency_object._calculate_base_total_difficulty()
        self.assertEqual(85, base_total_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_age_concurency = 0
        concurency_object.site_stem_concurency = 0
        concurency_object.site_volume_concurency = 0
        concurency_object.site_backlinks_concurency = 0
        concurency_object.importance = STANDART_IMPORTANCE
        base_total_concurency = concurency_object._calculate_base_total_difficulty()
        self.assertEqual(0, base_total_concurency)

        concurency_object = NRHUnitTestConcurency()
        concurency_object.site_age_concurency = 25
        concurency_object.site_stem_concurency = 50
        concurency_object.site_volume_concurency = 100
        concurency_object.site_backlinks_concurency = 100
        concurency_object.importance = STANDART_IMPORTANCE
        base_total_concurency = concurency_object._calculate_base_total_difficulty()
        self.assertEqual(55, base_total_concurency)

if __name__ == '__main__':
    unittest.main()
