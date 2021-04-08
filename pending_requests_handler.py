import lxml
import postgres_mode as pm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from threading import Thread
from conc_settings import *
import time

class Manager:
    def __init__(self):
        self.requests = tuple()
        self.yandex_objects_list = list()
        self.threads_list = ''


        self.get_requests_from_queue()
        self.make_threads()
        self.run_threads()
        self.check_threads()

        if len(self.requests) > 0:
            self.delete_requests_from_queue()

        print(f'Обработано {len(self.requests)} запросов ожидающих ссылок')

    def get_requests_from_queue(self):

        sql = ("SELECT request_id, request_text, xml, concurent_site.main_handledxml.status, geo "
               "FROM concurent_site.main_handledxml "
               "INNER JOIN concurent_site.main_request USING (request_id) "
               "WHERE concurent_site.main_handledxml.status = 'pending' "
               f"LIMIT 10;")

        items = pm.custom_request_to_database_with_return(sql)

        reqs = list()
        for item in items:
            reqs.append(item)

        self.requests = tuple(reqs)

    def create_yandex_object(self, request):
        self.yandex_objects_list.append(Yandex(request))

    def make_threads(self):
        self.threads_list = [Thread(target=self.create_yandex_object, args=(request,)) for request in self.requests]

    def run_threads(self):
        for thread in self.threads_list:
            thread.start()

    def check_threads(self):
        for thread in self.threads_list:
            thread.join()

    def delete_requests_from_queue(self):
        for yandex_object in self.yandex_objects_list:
            if yandex_object.concurency_object:
                if yandex_object.concurency_object.status == 'ready':
                    pm.custom_request_to_database_without_return(
                        f"DELETE FROM concurent_site.main_handledxml WHERE request_id = {yandex_object.request_id};"
                    )



class Yandex:
    def __init__(self, request):

        self.request_id = request[0]
        self.request = request[1]
        self.xml = request[2]
        self.geo = request[4]
        self.page_xml = ''
        self.site_list = list()
        self.site_objects_list = list()
        self.concurency_object = ''

        self.get_page_xml()
        self.get_site_list()
        if len(self.site_list) >= 15:
            self.clean_garbage()

            self.make_site_objects()
            if self.check_valid():
                self.make_concurency_object()
                self.update_database()
        else:
            print('Нужно фиксить XML')
            pass


    def get_page_xml(self):
        self.page_xml = BeautifulSoup(self.xml, 'lxml')

    def get_site_list(self):
        self.site_list = self.page_xml.find_all('doc')

    def clean_garbage(self):
        del self.xml
        del self.page_xml

    def make_site_objects(self):
        position = 1
        for site in self.site_list:
            url = site.find('url').text
            self.site_objects_list.append(Site(position, url))
            position += 1

    def check_valid(self):
        valid_backlinks = 0
        for site in self.site_objects_list:
            if site.domain_object.status == 'complete':
                valid_backlinks += 1

        if valid_backlinks == len(self.site_list):
            print(f'Валидных ссылок: {valid_backlinks} из {len(self.site_list)}. Все ОК')
            return True
        else:
            print(f'Валидных ссылок: {valid_backlinks} из {len(self.site_list)}. Все плохо')
            return False

    def make_concurency_object(self):
        self.concurency_object = Concurency(self.site_objects_list, self.request, self.geo, self.request_id)


    def update_database(self):

        pm.custom_request_to_database_without_return(
            f"UPDATE concurent_site.main_request SET "
            f"site_backlinks_concurency = {self.concurency_object.site_backlinks_concurency}, "
            f"site_seo_concurency = {self.concurency_object.site_seo_concurency}, "
            f"site_total_concurency = {self.concurency_object.site_total_concurency}, "
            f"average_unique_backlinks = {self.concurency_object.average_unique_backlinks}, "
            f"average_total_backlinks = {self.concurency_object.average_total_backlinks},"
            f"vital_sites = '{self.concurency_object.vital_domains}', "
            f"vital_sites_count =  {self.concurency_object.vital_domains_amount}, "
            f"status = 'ready' "
            f"WHERE request_id = {self.request_id}"
        )

class Site:
    def __init__(self, position, url):
        self.position = position
        self.url = url
        self.domain = ''
        self.domain_object = ''

        self.get_domain()
        self.make_domain_object()

    def get_domain(self):
        self.domain = urlparse(self.url)
        self.domain = self.domain.netloc
        self.domain.replace('www.', '')

        while self.domain.count('.') != 1:
            first_dot = self.domain.find('.') + 1
            self.domain = self.domain[first_dot:]

    def make_domain_object(self):
        self.domain_object = Domain(self.domain)

class Domain:
    def __init__(self, domain):
        self.domain = domain
        self.unique_backlinks = ''
        self.total_backlinks = ''
        self.backlinks_object = ''
        self.status = ''

        self.check_data_in_database()


    def check_data_in_database(self):
        check = pm.check_in_database('main_domain', 'name', self.domain)

        if check:
            self.domain_age = check[0][1]
            self.unique_backlinks = check[0][2]
            self.total_backlinks = check[0][3]
            self.status = check[0][4]
            self.domain_group = check[0][5]

        if self.status == '':
            test = self.domain.encode('utf-8')
            print(f'Внезапно потерялся {self.domain.encode("utf-8")}')
            values_to_go = (self.domain, 5, 0, 0, 'pending')
            pm.add_to_database('main_domain', values_to_go)

class Concurency:
    def __init__(self, site_objects_list, request, geo, request_id):
        self.request_id = request_id
        self.site_objects_list = site_objects_list
        self.request = request
        self.geo = geo
        self.WEIGHTS = dict()
        self.importance = dict()
        self.site_age_concurency = int()
        self.site_stem_concurency = int()
        self.site_volume_concurency = int()
        self.site_seo_concurency = int()
        self.site_direct_concurency = int()
        self.direct_upscale = int()
        self.status = ''
        self.site_backlinks_concurency = int()
        self.site_total_concurency = int()

        self.average_total_backlinks = int()
        self.average_unique_backlinks = int()
        self.vital_domains = list()
        self.vital_domains_amount = int()

        self.get_concurency_from_database()
        if self.check_is_absourd_request():
            self.importance = ABSURD_STEM_IMPORTANCE
        else:
            self.importance = STANDART_IMPORTANCE


        if self.direct_upscale > 0:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC


        self.calculate_site_backlinks_concurency()
        self.calculate_site_total_concurency()
        self.status = 'ready'
        self.update_report()
        self.convert_vital_domains_to_sting()

    def convert_vital_domains_to_sting(self):
        self.vital_domains_amount = len(self.vital_domains)
        self.vital_domains = ' '.join(self.vital_domains)


    def get_concurency_from_database(self):
        sql = ('SELECT '
               'site_age_concurency, site_stem_concurency, site_volume_concurency, direct_upscale '
               'FROM '
               'concurent_site.main_request '
               'WHERE '
               f"request_id = {self.request_id};")
        concurency =pm.custom_request_to_database_with_return(sql)[0]

        self.site_age_concurency = int(concurency[0])
        self.site_stem_concurency = int(concurency[1])
        self.site_volume_concurency = int(concurency[2])
        self.direct_upscale = int(concurency[3])

        if self.site_age_concurency == 0:
            print('ПОПАЛСЯ!')

    def check_is_absourd_request(self):
        if self.site_stem_concurency < 30:
            return True

    def calculate_site_backlinks_concurency(self):
        max_backlinks_concurency = 0
        real_backlinks_concurency = 0
        maximum_backlinks = 500

        total_total_backlinks = 0
        total_unique_backlinks = 0

        file = open(f'./reports/backs.txt', 'a', encoding='utf-8')
        file.write(f'\nДанные из пендинга\n')
        for site_object in self.site_objects_list:
            try:

                unique_backlinks = site_object.domain_object.unique_backlinks
                total_backlinks = site_object.domain_object.total_backlinks


                if site_object.domain_object.domain_group != 1:
                    total_unique_backlinks += unique_backlinks
                    total_total_backlinks += total_backlinks
                    file.write(f'Сайт: {site_object.domain}. Уников: {unique_backlinks}, Тотал: {total_backlinks} НЕ ВИТАЛЬНЫЙ\n')
                else:
                    file.write(f'Сайт: {site_object.domain}. Уников: {unique_backlinks}, Тотал: {total_backlinks} ВИТАЛЬНЫЙ\n')
                    if site_object.position <= 10:
                        self.vital_domains.append(site_object.domain)

                if unique_backlinks > maximum_backlinks:
                    unique_backlinks = maximum_backlinks
                real_backlinks_concurency += int(unique_backlinks / maximum_backlinks * 100 * self.WEIGHTS[str(site_object.position)])
                max_backlinks_concurency += 100 * self.WEIGHTS[str(site_object.position)]
            except:
                pass

        self.site_backlinks_concurency = int(real_backlinks_concurency / max_backlinks_concurency * 100)
        self.average_total_backlinks = int(total_total_backlinks / len(self.site_objects_list))
        self.average_unique_backlinks = int(total_unique_backlinks / len(self.site_objects_list))
        file.write(f'Всего уников {self.average_unique_backlinks}, Всего тотал {self.average_total_backlinks}\n')
        file.close()

    def calculate_site_total_concurency(self):
        total_difficulty = int(
            self.site_age_concurency * self.importance['Возраст сайта'] + self.site_stem_concurency * self.importance[
                'Стемирование'] + self.site_volume_concurency * self.importance[
                'Объем статей'] + self.site_backlinks_concurency * self.importance['Ссылочное'])
        self.site_seo_concurency = total_difficulty
        total_difficulty += self.direct_upscale
        self.site_total_concurency = total_difficulty

    def update_report(self):
        file = open(f'./reports/{self.request}.txt', 'a', encoding='utf-8')
        file.write('АПДЕЙТ ОТ ПЕНДИНГА\n')
        real_concurency = int()
        max_concurency = int()
        for site_object in self.site_objects_list:
            site_object.position = str(site_object.position)
            if site_object.domain_object.unique_backlinks > 500:
                site_object.domain_object.unique_backlinks = 500
            max_concurency += 500 * self.WEIGHTS[site_object.position]

            real_concurency += site_object.domain_object.unique_backlinks * self.WEIGHTS[site_object.position]
            file.write(f'Сайт: {site_object.domain}. Количество бэклинков: {site_object.domain_object.unique_backlinks}. Находится на {site_object.position} месте. Кэф {self.WEIGHTS[site_object.position]} Сложность повысилась на {site_object.domain_object.unique_backlinks * self.WEIGHTS[site_object.position]} из {500 * self.WEIGHTS[site_object.position]}\n')
        file.write(f'Уровень конкуренции от бэклинков: {real_concurency} из {max_concurency}. Процент: {int(real_concurency / max_concurency * 100)}. Значение в базе: {self.site_backlinks_concurency}\n')

        file.write(f'Итоговая конкуренция:\n')
        total_difficulty = int(
            self.site_age_concurency * self.importance['Возраст сайта'] + self.site_stem_concurency * self.importance[
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

        total_difficulty -= self.direct_upscale
        file.write(f'После вычета direct upscale ({self.direct_upscale}): {total_difficulty}\n')
        file.close()

if __name__ == '__main__':
    while True:
        Manager()
        time.sleep(20)