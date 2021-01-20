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
        items = pm.check_in_database('main_handledxml', 'status', 'pending', 4)
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
        reqs = list()
        for yandex_object in self.yandex_objects_list:
            if yandex_object.concurency_object:
                if yandex_object.concurency_object.status == 'ready':
                    reqs.append(yandex_object.request)
        reqs = tuple(reqs)
        pm.delete_from_database('main_handledxml', 'request', reqs)



class Yandex:
    def __init__(self, request):


        self.request = request[0]
        self.xml = request[1]
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
            if site.domain_object.backlinks != 0:
                valid_backlinks += 1

        if valid_backlinks == len(self.site_list):
            print(f'Валидных ссылок: {valid_backlinks} из {len(self.site_list)}. Все ОК')
            return True
        else:
            print(f'Валидных ссылок: {valid_backlinks} из {len(self.site_list)}. Все плохо')
            return False

    def make_concurency_object(self):
        self.concurency_object = Concurency(self.site_objects_list, self.request)


    def update_database(self):
        pm.update_database('main_request', 'site_backlinks_concurency',
                           self.concurency_object.site_backlinks_concurency, 'request', self.request)
        pm.update_database('main_request', 'site_total_concurency',
                           self.concurency_object.site_total_concurency, 'request', self.request)
        pm.update_database('main_request', 'status',
                           'ready', 'request', self.request)

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
        self.backlinks = ''
        self.backlinks_object = ''

        self.check_data_in_database()


    def check_data_in_database(self):
        check = pm.check_in_database('main_domain', 'name', self.domain)

        if check:
            self.domain_age = check[0][1]
            self.backlinks = check[0][2]

class Concurency:
    def __init__(self, site_objects_list, request):
        self.site_objects_list = site_objects_list
        self.request = request
        self.WEIGHTS = dict()
        self.site_age_concurency = int()
        self.site_stem_concurency = int()
        self.site_volume_concurency = int()
        self.direct_upscale = int()
        self.status = ''

        self.site_backlinks_concurency = int()
        self.site_total_concurency = int()

        self.get_concurency_from_database()

        if self.direct_upscale > 0:
            self.WEIGHTS = WEIGHTS_DIRECT
        else:
            self.WEIGHTS = WEIGHTS_ORGANIC

        self.calculate_site_backlinks_concurency()
        self.calculate_site_total_concurency()
        self.status = 'ready'

    def get_concurency_from_database(self):
        concurency = pm.check_in_database('main_request', 'request', self.request)[0]
        self.site_age_concurency = int(concurency[2])
        self.site_stem_concurency = int(concurency[3])
        self.site_volume_concurency = int(concurency[4])
        self.direct_upscale = int(concurency[7])


    def calculate_site_backlinks_concurency(self):
        max_backlinks_concurency = 0
        real_backlinks_concurency = 0
        maximum_backlinks = 500

        for site_object in self.site_objects_list:
            try:
                if site_object.domain_object.backlinks > maximum_backlinks:
                    site_object.domain_object.backlinks = maximum_backlinks
                real_backlinks_concurency += int(site_object.domain_object.backlinks / maximum_backlinks * 100 * self.WEIGHTS[str(site_object.position)])
                max_backlinks_concurency += 100 * self.WEIGHTS[str(site_object.position)]
            except:
                pass
        self.site_backlinks_concurency = int(real_backlinks_concurency / max_backlinks_concurency * 100)

    def calculate_site_total_concurency(self):
        total_difficulty = int(
            self.site_age_concurency * IMPORTANCE['Возраст сайта'] + self.site_stem_concurency * IMPORTANCE[
                'Стемирование'] + self.site_volume_concurency * IMPORTANCE[
                'Объем статей'] + self.site_backlinks_concurency * IMPORTANCE['Ссылочное'])
        total_difficulty += self.direct_upscale
        self.site_total_concurency = total_difficulty


if __name__ == '__main__':
    while True:
        Manager()
        time.sleep(20)