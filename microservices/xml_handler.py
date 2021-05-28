import requests
import time
from microservices import postgres_mode as pm
from threading import Thread
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Request:
    id: int
    text: str
    region_id: int
    xml_url: str = ''
    validated_text: str = ''
    status: str = ''
    refresh_timer: int = 0
    reruns_count: int = 0
    bottom_ads_count: int = 0
    top_ads_count: int = 0


class XmlReport:

    def __init__(self):
        self.requests = list()
        self.xml_answers = list()
        self.requests_in_work = list()
        self.thread_list = list()

        self.get_requests_from_queue()

        if len(self.requests) == 0:
            self.get_requests_for_recheck()
            if len(self.requests) != 0:
                self.make_xml_request_packs()
                self.update_reruns_for_recheck_requests()
                self.make_recheck_threads()
                self.run_threads()
                self.check_threads()
                self.update_ads_count_in_database()
            self.update_fully_rechecked_requests()
            self.delete_fully_rechecked_requests()
        else:
            self.make_xml_request_packs()
            self.make_threads()
            self.run_threads()
            self.check_threads()
            self.add_xml_answers_to_database()

        self.update_refresh_timer()



    def get_fully_rechecked_requests(self):
        """
        Собирает из БД все запросы, у которых произошло максимальное количество перепроверок
        Очень важно, что также учитывается статус запроса в таблице main_request
        Если бы такой дополнительной проверки не было, запросы могли бы удаляться из таблицы xml_handler до того,
        как их обработает new_requests_handler
        """
        sql = ("SELECT request_id, bottom_ads_count, top_ads_count "
               "FROM concurent_site.main_handledxml xml "
               "INNER JOIN concurent_site.main_request request "
               "ON (xml.request_id = request.id) "
               "WHERE request.status = 'ready' AND "
               "xml.reruns_count = 4;")

        rechecked_requests = pm.custom_request_to_database_with_return(sql)
        return rechecked_requests

    def get_direct_upscale_and_concurency(self, request):
        """
        direct_upscale - условные единицы повышения конкуренции по поисковому запросу из-за наличия рекламных блоков
        direct_concurency - рейтинг конкуренции, завязанный на процентгую шкалу. Считается с помощью деления
            накопленного direct upscale на 35 (максимально возможный upscale)

        Метод подсчитывает количество объявлений в верхней и нижней части страницы поисковой выдачи.
        У каждого из объявлений разный коэффицент важности. Объявление на первом месте поисковой выдачи гораздо важнее,
        чем то, что находится под результатами поиска. И гораздо больше влияет на конкуренцию.
        В нижней части страницы могут находиться максимум 5 объявлений, в верхней - 4. В сумме - 9.
        """
        direct_sites = request[1] + request[2]
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
            if direct_sites == 4:
                direct_upscale += 6.4
            elif direct_sites == 3:
                direct_upscale += 4.8
            elif direct_sites == 2:
                direct_upscale += 3.2
            elif direct_sites == 1:
                direct_upscale += 1.6

        direct_concurency = int(direct_upscale / 35 * 100)

        return direct_upscale, direct_concurency

    def update_fully_rechecked_requests(self):
        """
        В основной таблице main_request обновляется информация о direct upscale и direct concurency
        """
        rechecked_requests = self.get_fully_rechecked_requests()

        for request in rechecked_requests:
            request_id = request[0]
            direct_upscale, direct_concurency = self.get_direct_upscale_and_concurency(request)

            sql = ("UPDATE concurent_site.main_request "
                   f"SET direct_upscale = {direct_upscale}, "
                   f"is_direct_final = 1, "
                   f"site_direct_concurency = {direct_concurency} "
                   f"WHERE request_id = {request_id};")

            pm.custom_request_to_database_without_return(sql)

    def delete_fully_rechecked_requests(self):
        """
        Удаление их очереди всех запросов, по которым было выполнено максимальное количество перепроверок
        """
        sql = ("DELETE FROM concurent_site.main_handledxml xml "
               "USING concurent_site.main_request request "
               "WHERE request.id  = xml.request_id AND xml.reruns_count = 4 AND request.status = 'ready' "
               "RETURNING request.status;")

        pm.custom_request_to_database_without_return(sql)

    def update_ads_count_in_database(self):
        """
        Обновляется количество объявлений в базе данных по каждому запросу при перепроверке
        """
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
        """
        LIMIT 10 установлен из-за ограничений XML сервиса. Одновременно может работать
        не более 10 потоков
        """
        sql = ('SELECT request_id, text, queue.region_id '
               'FROM concurent_site.main_requestqueue queue '
               'INNER JOIN concurent_site.main_request request ON '
               '(queue.request_id = request.id) '
               'LIMIT 10;')

        database_return = pm.custom_request_to_database_with_return(sql)

        for data in database_return:
            request_data = Request(id=data[0], text=data[1], region_id=data[2])

            self.requests.append(request_data)

    def get_requests_for_recheck(self):
        """
        Сторонний XML сервис слишком часто показывает некорректные результаты, их необходимо перепроверять.
        Если в очереди закончились поисковые запросы пользователей, выполняется перепроверка результатов.
        На выходе получается кортеж, содержащий id запроса, текст запроса, id региона,
        количество пройденных итерация перепроверки, а также, максимальное количество  объявлений,
        которое было собрано в предыдущие обходы. Максимальное количество перепроверок - 3.
        """
        sql = (
            'SELECT request_id, text, xml.region_id, reruns_count, top_ads_count, bottom_ads_count, request.status '
            'FROM concurent_site.main_handledxml xml '
            'INNER JOIN concurent_site.main_request request '
            'ON (xml.request_id = request.id) '
            'WHERE refresh_timer < 0 AND reruns_count < 4'
            'LIMIT 10;')

        database_return = pm.custom_request_to_database_with_return(sql)

        for data in database_return:
            request_data = Request(id=data[0], text=data[1], region_id=data[2],
                                   reruns_count=data[3], top_ads_count=data[4],
                                   bottom_ads_count=data[5], status=data[6])

            self.requests.append(request_data)

    def make_xml_request_packs(self):
        """
        У стороннего XML сервиса есть особенность работы. У него есть "домашний" регион. Он указывается в админке.
        По умолчанию все запросы ищутся в этом регионе. Если необходимо узнать информацию о поисковом запросе в другом
        регионе, код региона нужно передать через GET запрос ?lr= . Но если совпадет так, что домашний регион
        идентичен тому, что передан в GET запросе, у XML сервиса происходит сбой и он вообще не показывает
        рекламные блоки в выдаче. Поэтому, через IF конструкцию происходит перепроврерка не совпадает ли регион
        запроса пользователя с регионом, указанным в админке.
        """
        for request_data in self.requests:
            if int(request_data.region_id) == 255:
                xml_url = f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_data.text}'
            else:
                xml_url = f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_data.text}&lr={request_data.region_id}'

            request_data.xml_url = xml_url

            print(request_data)

    def write_xmlurl_and_answer_to_log_file(self, request, raw_text):
        """
        Записывает в файл url XML запроса и ответ XML сервиса
        """
        file = open(f'./reports/{request.text}-{request.region_id}.txt', 'a', encoding='utf-8')
        file.write('----------------------------------------\n')
        file.write(f'{request.xml_url}\n')
        file.write('----------------------------------------\n')
        file.write(f'{raw_text}\n')

    def add_data_to_dataset(self, request, validated_text, refresh_timer, reruns_count, bottom_ads_count, top_ads_count):
        request.validated_text = validated_text
        request.status = 'in work'
        request.refresh_timer = refresh_timer
        request.reruns_count = reruns_count
        request.bottom_ads_count = bottom_ads_count
        request.top_ads_count = top_ads_count
        self.xml_answers.append(request)

    def get_xml_answer(self, request, rerun=0, previous_run_top_ads=0,
                       previous_run_bottom_ads=0):
        """

        """
        r = requests.get(request.xml_url)
        raw_text = r.text
        site_numbers = len(re.findall(r'<doc>', raw_text))

        self.write_xmlurl_and_answer_to_log_file(request, raw_text)

        if site_numbers > 15:
            validated_text, top_ads_count, bottom_ads_count = self.validate_xml_answer(raw_text)
            if top_ads_count + bottom_ads_count == 9:
                reruns_count = 4
                refresh_timer = 0
            else:
                reruns_count = 1
                refresh_timer = 10

            if 'Ответ от поисковой системы не получен' not in validated_text:
                if bottom_ads_count > 5:
                    top_ads_count = bottom_ads_count - 5
                    bottom_ads_count = bottom_ads_count - top_ads_count
                if not rerun:
                    self.add_data_to_dataset(request, validated_text, refresh_timer, reruns_count, bottom_ads_count, top_ads_count)
                else:
                    total_ads_count = top_ads_count + bottom_ads_count
                    previous_run_ads_count = previous_run_top_ads + previous_run_bottom_ads
                    if total_ads_count > previous_run_ads_count:
                        refresh_timer = 10
                        rerun += 1
                        self.add_data_to_dataset(request, validated_text, refresh_timer, reruns_count, bottom_ads_count,
                                                 top_ads_count)

            else:
                print(f'Ошибка XML в запросе {request}: {validated_text}')

    def count_ads(self, text):
        """
        Метод считает количество объявлений в верхней и нижней части страницы.
        Иногда, XML сервис работает некорректно и выдает сырые результаты. Поэтому, если на странице не найдено
        ни одно обявление, дополнительно проверяется наличие на странице стандартных ссылок яндекс директ yabs.yandex.ru
        Еще одна ошибка в работе внешнего XML сервиса - он часто ошибочно не разделяет объявления в верхней и
        нижней части, записывая все объявления в нижнюю часть. Всего может быть только 9 объявлений - 4 свеху и 5 снизу.
        Если в ответе XML сервиса, например, 7 объявлений снизу, то 2 объявления считаются "избыточными".
        """
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

    def edit_xml_answer_text(self, overcaped_ads_count, bottom_ads_block, text):
        """
        Из текста xml ответа вырезается текст избыточных объявлений и переносится в верхнюю часть документа
        внутрь тега <topads>
        """
        result = ''
        try:
            for n in range(overcaped_ads_count):
                result += str(bottom_ads_block[n])
        except:
            print('aa')

        text = text.replace(result, '')
        validated_text = '<topads>' + result + '</topads>' + text

        return validated_text

    def validate_xml_answer(self, text):
        """
        Валидация xml ответа напрямую связана с наличием в ответе xml сервиса избыточных объявлений
        (overcapped bottom ads count). Подробнее об этом описано в документации метода count_ads.
        Если избыточных объявлений нет, xml_answer считается валидированным.
        Если избыточные объявления есть, текст запроса редактируется и валидируется
        """
        overcaped_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block = self.count_ads(text)

        if overcaped_ads_count <= 0:
            return text, top_ads_count, bottom_ads_count

        if overcaped_ads_count > 0 and top_ads_count > 0:
            raise SystemError('В гарантии оверкап, но и наверху есть объявления')

        validated_text = self.edit_xml_answer_text(overcaped_ads_count, bottom_ads_block, text)

        return validated_text, top_ads_count, bottom_ads_count

    def make_threads(self):
        """
        В self.xml_request_packs лежат словари формата {(Ответ от базы данных):'ссылка для xml запроса'}
        Для каждого такого словаря создается объект Thread, в который передаются данные из БД и url для запроса
        """
        for request in self.requests:
            self.thread_list.append(
                Thread(target=self.get_xml_answer, args=(request,)))

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def delete_xml_answer_from_database(self, request_id):
        sql = ('DELETE FROM '
               'concurent_site.main_requestqueue '
               'WHERE '
               f"request_id={request_id};")
        pm.custom_request_to_database_without_return(sql)

    def add_xml_answers_to_database(self):
        for xml_answer in self.xml_answers:
            sql = ('INSERT INTO concurent_site.main_handledxml '
                   '(xml, status, refresh_timer, reruns_count, top_ads_count, bottom_ads_count, region_id, request_id)'
                   ' VALUES '
                   f"('{xml_answer.xml_url}', '{xml_answer.status}', '{xml_answer.refresh_timer}', '{xml_answer.reruns_count}',"
                   f"'{xml_answer.top_ads_count}', '{xml_answer.bottom_ads_count}', '{xml_answer.region_id}', '{xml_answer.id}')")
            pm.custom_request_to_database_without_return(sql)
            self.delete_xml_answer_from_database(xml_answer.id)

    def update_refresh_timer(self):
        """
        У всех запросов, где количество перепроверок меньше максимального, таймер до перепроверки уменьшается на 1.
        Таймер до перепроверки - это количество вызовов класса XmlReport. В одной из версий программы использовались
        таймстемпы, но отказался от них из-за лишних вычислений разницы между таймстемпами.
        """
        sql = ("UPDATE concurent_site.main_handledxml SET "
               "refresh_timer = refresh_timer - 1 "
               "WHERE reruns_count < 4;")

        pm.custom_request_to_database_without_return(sql)




    def make_recheck_threads(self):
        """
        В self.xml_request_packs лежат словари формата {(Ответ от базы данных):'ссылка для xml запроса'}
        Для каждого такого словаря создается объект Thread, в который передаются данные из БД и url для запроса
        """
        for xml_pack in self.requests:
            for request_pack, xml_url in xml_pack.items():
                request_id = request_pack[0]
                request_text = request_pack[1]
                geo = request_pack[2]
                reruns_count = request_pack[3]
                top_ads_count = request_pack[4]
                bottom_ads_count = request_pack[5]
                self.thread_list.append(
                    Thread(target=self.get_xml_answer, args=(
                    request_id, request_text, xml_url, geo, reruns_count, bottom_ads_count, top_ads_count)))

    def update_reruns_for_recheck_requests(self):
        """
        Счетчик перепроверок увеличивается на 1 и таймер перепроверки становится равен 10.
        """
        list_of_rechecking_requests_ids = [str(request[0]) for request in self.requests]
        requests_ids = ','.join(list_of_rechecking_requests_ids)
        sql = ("UPDATE concurent_site.main_handledxml SET "
               "reruns_count = reruns_count + 1, "
               "refresh_timer = 10 "
               f"WHERE request_id IN ({requests_ids})")

        pm.custom_request_to_database_without_return(sql)


while True:
    XmlReport()
    time.sleep(10)
