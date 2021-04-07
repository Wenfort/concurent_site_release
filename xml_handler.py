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
        print(f'Запускаю модуль перепроверки')
        self.update_refresh_timer()
        self.add_expired_domains_to_the_queue_again()

    def get_requests_from_queue(self):
        sql = ('SELECT request_id, request_text, region_id, is_recheck '  
               'FROM concurent_site.main_requestqueue '
               'INNER JOIN concurent_site.main_request USING (request_id) '
               'LIMIT 10;')

        self.requests = pm.custom_request_to_database_with_return(sql)

    def make_xml_request_packs(self):
        for request in self.requests:
            request_text = request[1]
            request_region = request[2]
            if int(request_region) == 255:
                xml_request_pack = {
                    request: f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_text}', }
            else:
                xml_request_pack = {
                    request: f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_text}&lr={request_region}', }

            self.xml_request_packs.append(xml_request_pack)
            print(xml_request_pack)
        self.xml_request_packs = tuple(self.xml_request_packs)

    def get_xml_answer(self, request_id, request, xml_url, geo, is_recheck):
        r = requests.get(xml_url)
        text = r.text
        site_numbers = len(re.findall(r'<doc>', text))

        file = open(f'./reports/{request}-{geo}.txt', 'a', encoding='utf-8')
        file.write('----------------------------------------\n')
        file.write(f'{xml_url}\n')
        file.write('----------------------------------------\n')
        file.write(f'{text}\n')

        if site_numbers > 15:
            if '<bottomads>' not in text and '<topads>' not in text:
                if is_recheck:
                    status = 'in work'
                    retry_timer = 0
                else:
                    status = 'no ads'
                    retry_timer = 11
            else:
                status = 'in work'
                retry_timer = 0

            if 'Ответ от поисковой системы не получен' not in text:
                self.xml_answers.append((text, status, geo, retry_timer, request_id))
            else:
                print(f'Ошибка XML в запросе {request}: {text}')

    def make_threads(self):
        for xml_pack in self.xml_request_packs:
            for request_pack, xml_url in xml_pack.items():
                request_id = request_pack[0]
                request_text = request_pack[1]
                geo = request_pack[2]
                is_recheck = request_pack[3]
                self.thread_list.append(
                    Thread(target=self.get_xml_answer, args=(request_id, request_text, xml_url, geo, is_recheck)))

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def delete_xml_answer_from_database(self, xml_answer):
        request_id = xml_answer[4]
        sql = ('DELETE FROM '
               'concurent_site.main_requestqueue '
               'WHERE '
               f"request_id={request_id};")
        pm.custom_request_to_database_without_return(sql)

    def add_xml_answers_to_database(self):
        for xml_answer in self.xml_answers:
            pm.add_to_database_with_autoincrement('main_handledxml', xml_answer)
            self.delete_xml_answer_from_database(xml_answer)

    def update_refresh_timer(self):
        sql = ("UPDATE concurent_site.main_handledxml SET "
               "refresh_timer = refresh_timer - 1 "
               "WHERE refresh_timer > 1 AND status = 'no ads';")
        pm.custom_request_to_database_without_return(sql)

    def add_expired_domains_to_the_queue_again(self):
        expired_requests = self.delete_expired_timer_requests_and_return_their_names()

        if expired_requests:
            exp_requests = ''
            for e_r in expired_requests:
                exp_requests += f'{e_r},'
            exp_requests = exp_requests[:-1]
            sql = f"INSERT INTO concurent_site.main_requestqueue(request_id, geo, is_recheck) VALUES {exp_requests}"
            pm.custom_request_to_database_without_return(sql)

    def delete_expired_timer_requests_and_return_their_names(self):
        sql = "DELETE FROM concurent_site.main_handledxml WHERE refresh_timer = 1 RETURNING request_id, geo, TRUE;"
        expired_requests = pm.custom_request_to_database_with_return(sql)

        return expired_requests


while True:
    XmlReport()
    time.sleep(10)
