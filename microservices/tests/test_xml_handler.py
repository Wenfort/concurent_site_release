import unittest
from microservices import postgres_mode as pm
from microservices.xml_handler import XmlReport as XHXmlReport
from microservices.xml_handler import Request
from bs4 import BeautifulSoup

class XHUnitTestXmlReport(XHXmlReport):
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
               f"(2, 'Коррекция зрения', 0, 0, 0, 0, 0, 0, 0, 0, 'in work', 0, 0, 0, 0, 0, '', 0, 0, 255, {order_id}),"
               f"(3, 'ФРК', 0, 0, 0, 0, 0, 0, 0, 0, 'in work', 0, 0, 0, 0, 0, '', 0, 0, 255, {order_id}),"
               f"(4, 'Smile', 0, 0, 0, 0, 0, 0, 0, 0, 'in work', 0, 0, 0, 0, 0, '', 0, 0, 255, {order_id})")

        pm.custom_request_to_database_without_return(sql)

        file = open("first_xml_answer", "r")
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
               f"(DEFAULT, '{xml}', 'in work', 0, 0, 0, 0, 255, 2),"
               f"(DEFAULT, '{xml}', 'in work', -1, 1, 0, 0, 255, 3),"
               f"(DEFAULT, '{xml}', 'in work', 0, 4, 0, 0, 255, 4)")

        pm.custom_request_to_database_without_return(sql)

        file = open("second_xml_answer", "r")
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
        handler_object = XHUnitTestXmlReport()
        handler_object.requests = list()
        handler_object.get_requests_from_queue()

        request = handler_object.requests[0]
        self.assertEqual('Lasik', request.text)

        request = handler_object.requests[1]
        self.assertEqual('Коррекция зрения', request.text)

    def test_get_requests_for_recheck(self):
        handler_object = XHUnitTestXmlReport()
        handler_object.requests = list()
        handler_object.get_requests_for_recheck()

        request = handler_object.requests[0]
        self.assertEqual('ФРК', request.text)

    def test_add_url_to_dataset(self):
        request_datasets = (Request(text='Lasik', region_id=255),
                            Request(text='ФРК', region_id=10))

        handler_object = XHUnitTestXmlReport()
        handler_object.requests = request_datasets
        handler_object.add_url_to_dataset()

        self.assertEqual(
            'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query=Lasik',
            handler_object.requests[0].xml_url)
        self.assertEqual(
            'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query=ФРК&lr=10',
            handler_object.requests[1].xml_url)

    def test_get_ads_block(self):
        file = open("first_xml_answer", "r")
        xml = file.read()
        file.close()

        xml = BeautifulSoup(xml, 'html.parser')
        handler_object = XHUnitTestXmlReport()
        _, ads_count = handler_object.get_ads_block(xml, 'topads')
        self.assertEqual(4, ads_count)

        handler_object = XHUnitTestXmlReport()
        _, ads_count = handler_object.get_ads_block(xml, 'bottomads')
        self.assertEqual(5, ads_count)

    def test_get_real_ads_count(self):
        handler_object = XHUnitTestXmlReport()
        overcaped_bottom_ads_count, bottom_ads_count, top_ads_count = handler_object.get_real_ads_count(9)
        self.assertEqual(5, bottom_ads_count)
        self.assertEqual(4, top_ads_count)
        self.assertEqual(4, overcaped_bottom_ads_count)

    def test_count_ads(self):
        file = open("first_xml_answer", "r")
        xml = file.read()
        file.close()

        handler_object = XHUnitTestXmlReport()
        overcaped_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block = handler_object.count_ads(xml)
        self.assertEqual(0, overcaped_ads_count)
        self.assertEqual(4, top_ads_count)
        self.assertEqual(5, bottom_ads_count)

        file = open("first_xml_answer_with_overcap", "r")
        xml = file.read()
        file.close()

        handler_object = XHUnitTestXmlReport()
        overcaped_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block = handler_object.count_ads(xml)
        self.assertEqual(4, overcaped_ads_count)
        self.assertEqual(4, top_ads_count)
        self.assertEqual(5, bottom_ads_count)

    def test_validate_quotes_for_sql(self):
        handler_object = XHUnitTestXmlReport()
        string = "Д'Артаньян"
        string_for_sql = handler_object.validate_quotes_for_sql(string)
        self.assertEqual("Д''Артаньян", string_for_sql)

    def test_edit_xml_answer_text(self):
        file = open("first_xml_answer_with_overcap", "r")
        xml = file.read()
        file.close()
        soup = BeautifulSoup(xml, 'html.parser')

        handler_object = XHUnitTestXmlReport()
        bottom_ads_block, _ = handler_object.get_ads_block(soup, 'bottomads')
        edited_xml_text = handler_object.edit_xml_answer_text(4, bottom_ads_block, xml)

        soup = BeautifulSoup(edited_xml_text, 'html.parser')
        top_ads = soup.find('topads')
        top_ads_count = len(top_ads.find_all('query'))
        bottom_ads = soup.find('bottomads')
        bottom_ads_count = len(bottom_ads.find_all('query'))

        self.assertEqual(9, edited_xml_text.count('<query>'))
        self.assertEqual(4, top_ads_count)
        self.assertEqual(5, bottom_ads_count)

        file = open("second_xml_answer_with_overcap", "r")
        xml = file.read()
        file.close()
        soup = BeautifulSoup(xml, 'html.parser')

        handler_object = XHUnitTestXmlReport()
        bottom_ads_block, _ = handler_object.get_ads_block(soup, 'bottomads')
        edited_xml_text = handler_object.edit_xml_answer_text(2, bottom_ads_block, xml)

        soup = BeautifulSoup(edited_xml_text, 'html.parser')
        top_ads = soup.find('topads')
        top_ads_count = len(top_ads.find_all('query'))
        bottom_ads = soup.find('bottomads')
        bottom_ads_count = len(bottom_ads.find_all('query'))

        self.assertEqual(7, edited_xml_text.count('<query>'))
        self.assertEqual(2, top_ads_count)
        self.assertEqual(5, bottom_ads_count)

        file = open("third_xml_answer_with_overcap", "r")
        xml = file.read()
        file.close()
        soup = BeautifulSoup(xml, 'html.parser')

        handler_object = XHUnitTestXmlReport()
        bottom_ads_block, _ = handler_object.get_ads_block(soup, 'bottomads')
        edited_xml_text = handler_object.edit_xml_answer_text(0, bottom_ads_block, xml)

        soup = BeautifulSoup(edited_xml_text, 'html.parser')
        top_ads = soup.find('topads')
        top_ads_count = len(top_ads.find_all('query'))
        bottom_ads = soup.find('bottomads')
        bottom_ads_count = len(bottom_ads.find_all('query'))

        self.assertEqual(5, edited_xml_text.count('<query>'))
        self.assertEqual(0, top_ads_count)
        self.assertEqual(5, bottom_ads_count)

    def test_get_refresh_timer_and_reruns_count(self):
        handler_object = XHUnitTestXmlReport()
        reruns_count, refresh_timer = handler_object.get_refresh_timer_and_reruns_count(4, 5)
        self.assertEqual(4, reruns_count)
        self.assertEqual(0, refresh_timer)

        reruns_count, refresh_timer = handler_object.get_refresh_timer_and_reruns_count(4, 4)
        self.assertEqual(1, reruns_count)
        self.assertEqual(10, refresh_timer)

        self.assertRaises(ValueError, handler_object.get_refresh_timer_and_reruns_count, 14, 5)

    def test_is_rerun(self):

        handler_object = XHUnitTestXmlReport()
        request = Request(reruns_count=0)
        is_rerun = handler_object.check_is_rerun(request)
        self.assertEqual(None, is_rerun)

        request = Request(reruns_count=2)
        is_rerun = handler_object.check_is_rerun(request)
        self.assertEqual(True, is_rerun)

    def test_found_more_ads_then_before(self):

        handler_object = XHUnitTestXmlReport()
        request = Request(top_ads_count=4, bottom_ads_count=5)
        found_more = handler_object.check_found_more_ads_then_before(request, 4, 5)
        self.assertEqual(None, found_more)

        handler_object = XHUnitTestXmlReport()
        request = Request(top_ads_count=4, bottom_ads_count=5)
        found_more = handler_object.check_found_more_ads_then_before(request, 3, 4)
        self.assertEqual(None, found_more)

        handler_object = XHUnitTestXmlReport()
        request = Request(top_ads_count=0, bottom_ads_count=5)
        found_more = handler_object.check_found_more_ads_then_before(request, 1, 5)
        self.assertEqual(True, found_more)

    def test_finalize_dataset(self):
        handler_object = XHUnitTestXmlReport()
        request = Request()
        handler_object.finalize_dataset(request, 'hello', 10, 1, 5, 4)
        self.assertEqual('hello', request.validated_text)
        self.assertEqual('in work', request.status)
        self.assertEqual(10, request.refresh_timer)
        self.assertEqual(1, request.reruns_count)
        self.assertEqual(4, request.top_ads_count)
        self.assertEqual(5, request.bottom_ads_count)