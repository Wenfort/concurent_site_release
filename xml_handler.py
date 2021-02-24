import requests
import time
import postgres_mode as pm
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
        self.requests = pm.get_data_from_database('main_requestqueue', 10)

    def make_xml_request_packs(self):
        for request in self.requests:
            request_text = request[1]
            request_region = request[2]
            self.xml_request_packs.append(
                {
                    request: f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_text}&lr={request_region}',
                }
            )

            print(f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_text}&lr={request_region}')
        self.xml_request_packs = tuple(self.xml_request_packs)

    def get_xml_answer(self, request, xml_url, geo):
        r = requests.get(xml_url)
        text = r.text
        site_numbers = len(re.findall(r'<doc>', text))

        file = open(f'./reports/{request}-{geo}.txt', 'a', encoding='utf-8')
        file.write('----------------------------------------\n')
        file.write(f'{xml_url}\n')
        file.write('----------------------------------------\n')
        file.write(f'{text}\n')

        if site_numbers > 15:
            content_for_bs4 = text
            if 'Ответ от поисковой системы не получен' not in text:
                self.xml_answers.append((request, text, 'in work', geo))
            else:
                print(f'Ошибка XML в запросе {request}: {text}')

    def make_threads(self):
        for xml_pack in self.xml_request_packs:
            for request_pack, xml_url in xml_pack.items():
                request_text = request_pack[1]
                geo = request_pack[2]
                self.thread_list.append(Thread(target=self.get_xml_answer, args=(request_text, xml_url, geo)))

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def delete_xml_answer_from_database(self, xml_answer):
        request_text = xml_answer[0]
        geo = xml_answer[3]
        sql = ('DELETE FROM '
               'concurent_site.main_requestqueue '
               'WHERE '
               f"request_text='{request_text}' AND geo='{geo}';")
        pm.custom_request_to_database_without_return(sql)

    def add_xml_answers_to_database(self):
        for xml_answer in self.xml_answers:
            pm.add_to_database_with_autoincrement('main_handledxml', xml_answer)
            self.delete_xml_answer_from_database(xml_answer)


while True:
    XmlReport()
    time.sleep(10)