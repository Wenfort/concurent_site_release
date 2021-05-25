import requests
import time
from microservices import postgres_mode as pm
from threading import Thread
import re
from bs4 import BeautifulSoup


class XmlReport():

    def __init__(self):
        self.start = time.time()
        self.requests = tuple()
        self.xml_request_packs = list()
        self.xml_answers = list()
        self.requests_in_work = list()
        self.thread_list = list()
        self.deleted_requests = tuple()

        self.get_requests_from_queue()
        if len(self.requests) == 0:
            print(f'Задачи не обнаружены, запускаю модуль перепроверки')
            self.get_requests_for_recheck()
            if len(self.requests) != 0:
                self.update_reruns_for_recheck_requests()
                self.make_xml_request_packs()
                self.make_recheck_threads()
                self.run_threads()
                self.check_threads()
                self.update_ads_count_in_database()
            self.update_fully_rechecked_requests()
            self.deleted_requests = self.delete_fully_rechecked_requests()
        else:
            self.make_xml_request_packs()
            self.make_threads()
            self.run_threads()
            self.check_threads()
            self.add_xml_answers_to_database()
            print(f'{len(self.requests)} запроса собраны за {time.time() - self.start} секунд')

        self.update_refresh_timer()

    def update_fully_rechecked_requests(self):
        sql = ("SELECT request_id, bottom_ads_count, top_ads_count "
               "FROM concurent_site.main_handledxml xml "
               "INNER JOIN concurent_site.main_request req "
               "USING (request_id) "
               "WHERE req.status = 'ready' AND "
               "xml.reruns_count = 4;")

        rechecked_requests = pm.custom_request_to_database_with_return(sql)

        for req in rechecked_requests:
            request_id = req[0]
            direct_sites = req[1] + req[2]
            direct_upscale = 0

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

            direct_concurency = int(direct_upscale / 35 * 100)

            sql = ("UPDATE concurent_site.main_request "
                   f"SET direct_upscale = {direct_upscale}, "
                   f"is_direct_final = 1, "
                   f"site_direct_concurency = {direct_concurency} "
                   f"WHERE request_id = {request_id};")

            pm.custom_request_to_database_without_return(sql)

    def delete_fully_rechecked_requests(self):
        sql = ("DELETE FROM concurent_site.main_handledxml xml "
               "USING concurent_site.main_request req "
               "WHERE req.request_id  = xml.request_id AND xml.reruns_count = 4 AND req.status = 'ready' "
               "RETURNING req.status;")


        deleted_requests = pm.custom_request_to_database_with_return(sql)
        return deleted_requests

    def update_ads_count_in_database(self):
        for xml_answer in self.xml_answers:
            text = xml_answer[0]
            request_id = xml_answer[4]
            bottom_ads = xml_answer[6]
            top_ads = xml_answer[7]
            sql = ("UPDATE concurent_site.main_handledxml "
                   f"SET bottom_ads_count = {bottom_ads}, "
                   f"top_ads_count = {top_ads},"
                   f"xml = '{text}' "
                   f"WHERE request_id = {request_id}")

            pm.custom_request_to_database_without_return(sql)



    def get_requests_from_queue(self):
        sql = ('SELECT request_id, request_text, region_id '
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

    def get_xml_answer(self, request_id, request, xml_url, geo, rerun=0, previous_run_top_ads=0, previous_run_bottom_ads=0):
        r = requests.get(xml_url)
        text = r.text
        site_numbers = len(re.findall(r'<doc>', text))

        file = open(f'./reports/{request}-{geo}.txt', 'a', encoding='utf-8')
        file.write('----------------------------------------\n')
        file.write(f'{xml_url}\n')
        file.write('----------------------------------------\n')
        file.write(f'{text}\n')

        if site_numbers > 15:
            text, top_ads_count, bottom_ads_count = self.validate_xml_answer(text, rerun)
            if top_ads_count + bottom_ads_count == 9:
                reruns_count = 4
                refresh_timer = 0
            else:
                reruns_count = 1
                refresh_timer = 10

            if 'Ответ от поисковой системы не получен' not in text:
                if bottom_ads_count > 5:
                    top_ads_count = bottom_ads_count - 5
                    bottom_ads_count = bottom_ads_count - top_ads_count
                if not rerun:
                    self.xml_answers.append((text, 'in work', geo, refresh_timer, request_id, reruns_count, bottom_ads_count, top_ads_count))
                else:
                    total_ads_count = top_ads_count + bottom_ads_count
                    previous_run_ads_count = previous_run_top_ads + previous_run_bottom_ads
                    if total_ads_count > previous_run_ads_count:
                        refresh_timer = 10
                        rerun += 1
                        self.xml_answers.append((text, 'in work', geo, refresh_timer, request_id, rerun,
                                                 bottom_ads_count, top_ads_count))

            else:
                print(f'Ошибка XML в запросе {request}: {text}')

    def count_ads(self, text, rerun):
        soup = BeautifulSoup(text, 'html.parser')

        try:
            top_ads_block = soup.find('topads')
            top_ads_block = top_ads_block.find_all('query')
        except:
            top_ads_block = ''

        try:
            bottom_ads_block = soup.find('bottomads')
            bottom_ads_block = bottom_ads_block.find_all('query')
        except:
            bottom_ads_block = ''

        top_ads_count = len(top_ads_block)
        bottom_ads_count = len(bottom_ads_block)

        if not top_ads_block and not bottom_ads_block:
            bottom_ads_count = text.count('yabs.yandex.ru')

        overcaped_bottom_ads_count = bottom_ads_count - 5

        return overcaped_bottom_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block

    def validate_xml_answer(self, text, rerun):
        overcaped_bottom_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block = self.count_ads(text, rerun)

        if overcaped_bottom_ads_count <= 0:
            return text, top_ads_count, bottom_ads_count

        if overcaped_bottom_ads_count > 0 and top_ads_count > 0:
            raise SystemError('В гарантии оверкап, но и наверху есть объявления')

        result = ''
        try:
            for n in range(overcaped_bottom_ads_count):
                result += str(bottom_ads_block[n])
        except:
            print('aa')

        text = text.replace(result, '')
        validated_text = '<topads>' + result + '</topads>' + text

        return validated_text, top_ads_count, bottom_ads_count





    def make_threads(self):
        for xml_pack in self.xml_request_packs:
            for request_pack, xml_url in xml_pack.items():
                request_id = request_pack[0]
                request_text = request_pack[1]
                geo = request_pack[2]
                self.thread_list.append(
                    Thread(target=self.get_xml_answer, args=(request_id, request_text, xml_url, geo)))

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
               "WHERE reruns_count < 4;")
        pm.custom_request_to_database_without_return(sql)

    def get_requests_for_recheck(self):
        sql = ('SELECT request_id, request_text, region_id, reruns_count, top_ads_count, bottom_ads_count, main_request.status '
               'FROM concurent_site.main_handledxml '
               'INNER JOIN concurent_site.main_request USING (request_id) '
               'WHERE refresh_timer < 0 AND reruns_count < 4'
               'LIMIT 10;')

        self.requests = pm.custom_request_to_database_with_return(sql)

    def make_recheck_threads(self):
        for xml_pack in self.xml_request_packs:
            for request_pack, xml_url in xml_pack.items():
                request_id = request_pack[0]
                request_text = request_pack[1]
                geo = request_pack[2]
                reruns_count = request_pack[3]
                top_ads_count = request_pack[4]
                bottom_ads_count = request_pack[5]
                self.thread_list.append(
                    Thread(target=self.get_xml_answer, args=(request_id, request_text, xml_url, geo, reruns_count, bottom_ads_count, top_ads_count)))

    def update_reruns_for_recheck_requests(self):
        reqs = [str(req[0]) for req in self.requests]
        reqs = ','.join(reqs)
        sql = ("UPDATE concurent_site.main_handledxml SET "
               "reruns_count = reruns_count + 1, "
               "refresh_timer = 10 "
               f"WHERE request_id IN ({reqs})")

        pm.custom_request_to_database_without_return(sql)

while True:
    XmlReport()
    time.sleep(10)
