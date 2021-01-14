import requests
import time
import sqlite_mode as sm
from threading import Thread
import re


class XmlReport():

    def __init__(self):
        self.start = time.time()
        self.requests = tuple()
        self.xml_request_packs = list()
        self.xml_answers = list()
        self.requests_in_work = list()
        self.thread_list = list()

        self.get_requests_from_queue()
        self.make_xml_request_packs()


        self.make_threads()
        self.run_threads()
        self.check_threads()
        self.add_xml_answers_to_database()
        print(f'{len(self.requests)} запроса собраны за {time.time() - self.start} секунд')

    def get_requests_from_queue(self):
        self.requests = sm.get_data_from_database('db.sqlite3', 'main_requestqueue', 10)

    def make_xml_request_packs(self):
        for request in self.requests:
            request = request[0]
            self.xml_request_packs.append({
                                              request: f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request}'})

        self.xml_request_packs = tuple(self.xml_request_packs)

    def get_xml_answer(self, request, xml_url):
        r = requests.get(xml_url)
        text = r.text
        site_numbers = len(re.findall(r'<doc>', text))

        if site_numbers > 15:
            content_for_bs4 = r.content
            if 'Ответ от поисковой системы не получен' not in text:
                self.xml_answers.append({request: content_for_bs4})
            else:
                print(f'Ошибка XML в запросе {request}: {text}')

    def make_threads(self):
        for xml_pack in self.xml_request_packs:
            for request, xml_url in xml_pack.items():
                self.thread_list.append(Thread(target=self.get_xml_answer, args=(request, xml_url)))

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def add_xml_answers_to_database(self):
        requests_for_deletion = list()
        for xml_answer in self.xml_answers:
            for request, answer in xml_answer.items():
                requests_for_deletion.append(request)
                sm.add_to_database('db.sqlite3', 'main_handledxml', (request, answer, 'in work'))

        requests_for_deletion = tuple(requests_for_deletion)
        sm.delete_from_database('db.sqlite3', 'main_requestqueue', 'request', requests_for_deletion)


while True:
    XmlReport()
    time.sleep(10)
