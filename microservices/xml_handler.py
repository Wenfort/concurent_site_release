import requests
import time
from microservices import postgres_mode as pm
from threading import Thread
import re
from bs4 import BeautifulSoup
from microservices.microservices_dataclasses import XmlRequest


class XmlReport:

    def __init__(self):
        """
        Класс сначала проверяет есть ли запросы в очереди и обрабатывает их. Если запросы не найдены, происходит
            перепроврка запросов с подозрительными результатами. Подробнее - в комментариях к методам.
        """
        self.requests = list()
        self.thread_list = list()

        self.get_requests_from_queue()
        if self.requests:
            self.add_url_to_dataset()
            self.run_threads()
            self.add_xml_answers_to_database()
        else:
            self.get_requests_for_recheck()
            self.add_url_to_dataset()
            self.run_threads()
            self.update_reruns_for_recheck_requests()
            self.update_fully_rechecked_requests()
            self.delete_fully_rechecked_requests()

        self.update_refresh_timer()

    def get_fully_rechecked_requests(self):
        """
        Собирает из БД все запросы, у которых прошло максимальное количество перепроверок
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
                   f"direct_concurency = {direct_concurency} "
                   f"WHERE id = {request_id};")

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

    @staticmethod
    def update_ads_count_in_database(request):
        """
        Обновляется количество объявлений в базе данных по каждому запросу при перепроверке
        """
        sql = ("UPDATE concurent_site.main_handledxml "
               f"SET bottom_ads_count = {request.bottom_ads_count}, "
               f"top_ads_count = {request.top_ads_count},"
               f"xml = '{request.validated_text}' "
               f"WHERE request_id = {request.id}")

        pm.custom_request_to_database_without_return(sql)

    def get_requests_from_queue(self):
        """
        Метод берет данные из БД и кладет их в датасет, который будет дополняться в ходе выполнения инструкций.
        LIMIT 10 установлен из-за ограничений XML сервиса. Одновременно может работать не более 10 потоков.
        """
        sql = ('SELECT request_id, text, queue.region_id '
               'FROM concurent_site.main_requestqueue queue '
               'INNER JOIN concurent_site.main_request request ON '
               '(queue.request_id = request.id) '
               'LIMIT 10;')

        database_return = pm.custom_request_to_database_with_return(sql)

        for data in database_return:
            request_data = XmlRequest(id=data[0], text=data[1], region_id=data[2])

            self.requests.append(request_data)

    def get_requests_for_recheck(self):
        """
        Сторонний XML сервис слишком часто показывает некорректные результаты, их нужно перепроверять.
        Перепроверка начинается только если в очереди больше нет новых запросов от пользователей.
        После первой проверки пользователь уже будет видеть в личном кабинете предварительные данные,
        которые в 80% случаев верны. 100% точность достигается после 4 перепроверок (reruns_count) с интервалом в
        10 итераций запуска программы (refresh_timer).
        Средняя итерация занимает 45 секунд. Так что средняя перероверка происходит раз 8 минут.
        Я отказался от переобхода по разнице timezone.now(), т.к. хранить число от 1 до 10 проще, чем даты.
        И не нужно каждый раз высчитывать разницу между датами.
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
            request_data = XmlRequest(id=data[0], text=data[1], region_id=data[2],
                                      reruns_count=data[3], top_ads_count=data[4],
                                      bottom_ads_count=data[5], status=data[6])

            self.requests.append(request_data)

    def add_url_to_dataset(self):
        """
        У стороннего XML сервиса есть особенность работы. У него есть "домашний" регион. Он указывается в админке.
        По умолчанию все запросы ищутся в этом регионе. Если необходимо узнать информацию о поисковом запросе в другом
        регионе, код региона нужно передать через GET запрос ?lr= . Но если совпадет так, что домашний регион
        идентичен тому, что передан в GET запросе, у XML сервиса происходит сбой и он вообще не показывает
        рекламные блоки в выдаче. Поэтому, через IF конструкцию происходит перепроврерка не совпадает ли регион
        запроса пользователя с регионом, указанным в админке. После этого к датасету добавляется url для xml запроса
        """
        for request_data in self.requests:
            if request_data.region_id == 255:
                xml_url = f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_data.text}'
            else:
                xml_url = f'http://xmlriver.com/search_yandex/xml?user=1391&key=893df7feb2a0f02343085ea6bc9e5424056aa945&query={request_data.text}&lr={request_data.region_id}'

            request_data.xml_url = xml_url

    @staticmethod
    def write_to_log_file(request, *args):
        file = open(f'./reports/{request.text}-{request.region_id}.txt', 'a', encoding='utf-8')
        for arg in args:
            file.write('----------------------------------------\n')
            file.write(f'{arg}\n')

    @staticmethod
    def finalize_dataset(request, validated_text, refresh_timer, reruns_count, bottom_ads_count, top_ads_count):
        request.validated_text = validated_text
        request.status = 'in work'
        request.refresh_timer = refresh_timer
        request.reruns_count = reruns_count
        request.bottom_ads_count = bottom_ads_count
        request.top_ads_count = top_ads_count

    @staticmethod
    def get_refresh_timer_and_reruns_count(top_ads_count, bottom_ads_count):
        """
        Всего на странице может быть только 9 объявлений. Если в XML ответе их именно столько, дальнейшие
        перепроверки не требуются. Иначе - задаем стартовые данные для того, чтобы передать этот запрос на перепроверку
        """
        total_ads_count = top_ads_count + bottom_ads_count
        if total_ads_count > 9 or total_ads_count < 0:
            raise ValueError('Столько объявлений быть не может')
        elif total_ads_count == 9:
            reruns_count = 4
            refresh_timer = 0
        else:
            reruns_count = 1
            refresh_timer = 10

        return reruns_count, refresh_timer

    @staticmethod
    def check_found_more_ads_then_before(request, top_ads_count, bottom_ads_count):

        this_run_total_ads_count = top_ads_count + bottom_ads_count
        maximum_run_ads_count = request.bottom_ads_count + request.top_ads_count

        if this_run_total_ads_count > maximum_run_ads_count:
            return True

    def get_xml_answer(self, xml_url):
        r = requests.get(xml_url)

        return r.text

    @staticmethod
    def check_is_rerun(request):
        if request.reruns_count:
            return True

    def make_final_dataset(self, request):
        """
        Метод собирает недостающие данные для финального датасета.
        1) Получает данные от XML сервиса
        2) Записывает ответ в лог файл
        3) Считает количество сайтов от ответе XML сервиса. Если их больше 15, то ответ считается достоверным
        4) Обрабатываются известные ошибки и баги в ответе XML сервиса с помощью метода validate_xml_answer
        5) Если это первый обход запроса, то данные отправляются в БД.
        6) Если это перепроверка, то сначала происходит уточнение, было ли во время перепроверки найдено больше
            объявлений, чем в предыдущих обходах
        7) Если объявлений действительно больше, то эти данные заносятся в БД. Иначе- ничего.
        """
        raw_xml_text = self.get_xml_answer(request.xml_url)
        self.write_to_log_file(request, request.xml_url, raw_xml_text)

        site_number = len(re.findall(r'<doc>', raw_xml_text))

        if site_number > 15:
            validated_text, top_ads_count, bottom_ads_count, overcaped_ads_count = self.validate_xml_answer(
                raw_xml_text)
            reruns_count, refresh_timer = self.get_refresh_timer_and_reruns_count(top_ads_count, bottom_ads_count)

            if 'Ответ от поисковой системы не получен' not in validated_text:
                if self.check_is_rerun(request):
                    if self.check_found_more_ads_then_before(request, top_ads_count, bottom_ads_count):
                        self.finalize_dataset(request, validated_text, refresh_timer, reruns_count, bottom_ads_count,
                                              top_ads_count)

                        self.update_ads_count_in_database(request)
                else:
                    self.finalize_dataset(request, validated_text, refresh_timer,
                                          reruns_count, bottom_ads_count, top_ads_count)

            else:
                error_text = f'Ответ от поисковой системы не получен {request}: {validated_text}'
                self.write_to_log_file(request, error_text)

    @staticmethod
    def get_ads_block(soup, placement):
        """
        Принимает два placement:
        'topads' - объявления в верхней части страницы (спецразмещение)
        'bottomads' - объявления в нижней части страницы (гарантия)
        Позже будет добавлена 'rightads' - объявления справа. Яндекс тестирует этот тип.
        Если объявления не найдены, что случается часто, через exception возвращается пустая строка.
        """
        try:
            ads_block = soup.find(placement)
            ads_block = ads_block.find_all('query')
        except:
            ads_block = ''

        ads_count = len(ads_block)

        return ads_block, ads_count

    @staticmethod
    def get_real_ads_count(bottom_ads_count):
        """
        Еще одна ошибка в работе внешнего XML сервиса - он часто ошибочно не разделяет объявления в верхней и
        нижней части, записывая все объявления в нижнюю. Всего может быть только 9 объявлений - 4 свеху и 5 снизу.
        Если в ответе XML сервиса, например, 7 объявлений снизу, то 2 объявления считаются "избыточными".
        На самом деле, "избыточные" объявления - это объявления из верхней части страницы, по ошибке попавшие в нижнюю.
        """
        overcaped_bottom_ads_count = bottom_ads_count - 5
        top_ads_count = overcaped_bottom_ads_count
        bottom_ads_count = bottom_ads_count - overcaped_bottom_ads_count

        return overcaped_bottom_ads_count, bottom_ads_count, top_ads_count

    def count_ads(self, text):
        """
        Метод считает количество объявлений в верхней и нижней части страницы.
        Иногда, XML сервис работает некорректно и выдает сырые результаты. Их может быть как больше, так и меньше.
        Поэтому, если на странице не найдено ни одно обявление, дополнительно проверяется наличие на странице
        стандартных ссылок яндекс директ yabs.yandex.ru. Если же объявлений больше, чем вообще может быть,
        их реальное количество уточняет метод get_real_ads_count
        """
        soup = BeautifulSoup(text, 'html.parser')

        top_ads_block, top_ads_count = self.get_ads_block(soup, 'topads')
        bottom_ads_block, bottom_ads_count = self.get_ads_block(soup, 'bottomads')

        if not top_ads_block and not bottom_ads_block:
            bottom_ads_count = text.count('yabs.yandex.ru')

        if bottom_ads_count > 5:
            overcaped_ads_count, bottom_ads_count, top_ads_count = self.get_real_ads_count(bottom_ads_count)
        else:
            overcaped_ads_count = 0

        return overcaped_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block

    @staticmethod
    def edit_xml_answer_text(overcaped_ads_count, bottom_ads_block, text):
        """
        В переменной bottom_ads_block находится список рекламных блоков, находящихся в нижней части страницы.
        Метод вырезает их блока избыточные объявления и переносит их верхнюю часть документа внутрь тега <topads>.
        """
        overcaped_ads_block_text = ''

        for i in range(overcaped_ads_count):
            overcaped_ads_block_text += str(bottom_ads_block[i]) + '\n'

        text = text.replace(overcaped_ads_block_text, '')
        validated_text = '<topads>' + overcaped_ads_block_text + '</topads>' + text

        return validated_text

    @staticmethod
    def validate_quotes_for_sql(raw_xml):
        """
        Экранирует кавычки для добавления в БД
        """
        return raw_xml.replace("'", "''")

    def validate_xml_answer(self, raw_xml):
        """
        Метод валидирует разные данные:
        1) Количество объявлений в выдаче XML сервиса. Иногда, оно некорректно.
        2) Экранирует кавычки для отправки xml ответа в БД
        3) Редактирует XML файл если была найдена ошибка в количестве объявлений
        """
        overcaped_ads_count, top_ads_count, bottom_ads_count, bottom_ads_block = self.count_ads(raw_xml)

        validated_text = self.validate_quotes_for_sql(raw_xml)
        if overcaped_ads_count <= 0:
            return validated_text, top_ads_count, bottom_ads_count, overcaped_ads_count

        validated_text = self.edit_xml_answer_text(overcaped_ads_count, bottom_ads_block, validated_text)

        return validated_text, top_ads_count, bottom_ads_count, overcaped_ads_count

    def make_threads(self):
        """
        Для каждого датасета создается отдельный поток, в котором собираются недостающие данные
        """
        for request in self.requests:
            self.thread_list.append(
                Thread(target=self.make_final_dataset, args=(request,)))

    def run_threads(self):
        self.make_threads()
        self.start_threads()
        self.check_threads()

    def start_threads(self):
        for thread in self.thread_list:
            thread.start()

    def check_threads(self):
        for thread in self.thread_list:
            thread.join()

    def delete_xml_answer_from_queue(self, request_id):
        """
        Обработанные запросы после первого обхода удаляются из очереди. Перепроверки будут использовать данные
        из другой таблццы
        """

        sql = ('DELETE FROM '
               'concurent_site.main_requestqueue '
               'WHERE '
               f"request_id={request_id};")

        pm.custom_request_to_database_without_return(sql)

    def add_xml_answers_to_database(self):
        for request_dataset in self.requests:
            sql = ('INSERT INTO concurent_site.main_handledxml '
                   '(xml, status, refresh_timer, reruns_count, top_ads_count, bottom_ads_count, region_id, request_id)'
                   ' VALUES '
                   f"('{request_dataset.validated_text}', '{request_dataset.status}', '{request_dataset.refresh_timer}', '{request_dataset.reruns_count}',"
                   f"'{request_dataset.top_ads_count}', '{request_dataset.bottom_ads_count}', '{request_dataset.region_id}', '{request_dataset.id}')")
            pm.custom_request_to_database_without_return(sql)

            self.delete_xml_answer_from_queue(request_dataset.id)

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

    def update_reruns_for_recheck_requests(self):
        """
        Счетчик перепроверок увеличивается на 1 и таймер перепроверки становится равен 10.
        """
        list_of_rechecking_requests_ids = [str(request.id) for request in self.requests]
        requests_ids = ','.join(list_of_rechecking_requests_ids)
        sql = ("UPDATE concurent_site.main_handledxml SET "
               "reruns_count = reruns_count + 1, "
               "refresh_timer = 10 "
               f"WHERE request_id IN ({requests_ids})")

        pm.custom_request_to_database_without_return(sql)

if __name__ == "__main__":
    while True:
        XmlReport()
        print('Готово!')
        time.sleep(10)
