from microservices import postgres_mode as pm
from threading import Thread
import time
from microservices.new_requests_handler import RequestDataSet, Yandex, Site, Concurency


class Manager:
    def __init__(self):
        self.requests = list()
        self.yandex_objects_list = list()
        self.threads_list = list()

        self.get_requests_from_queue()
        self.run_threads()


    def run_threads(self):
        """
        Создает процессы, кладет в каждый из них датасет и объект класса Queue для извлечения данных.
        Затем запускает эти процессы и ожидает получение данных от Queue
        """
        self.make_threads()
        self.start_threads()
        self.check_threads()

    def get_requests_from_queue(self):

        sql = ("SELECT request_id, text, xml, xml.status, xml.region_id "
               "FROM concurent_site.main_handledxml xml "
               "INNER JOIN concurent_site.main_request req "
               "ON (xml.request_id = req.id) "
               "WHERE xml.status = 'pending' "
               f"LIMIT 10;")

        database_return = pm.custom_request_to_database_with_return(sql)

        for data in database_return:
            request_dataset = RequestDataSet(id=data[0], text=data[1], xml=data[2],
                                             xml_status=data[3], region_id=data[4])

            self.requests.append(request_dataset)

        self.requests = tuple(self.requests)

    def create_yandex_object(self, request_dataset):
        PendingRequestYandex(request_dataset)

    def make_threads(self):
        self.threads_list = [Thread(target=self.create_yandex_object, args=(request_dataset,))
                             for request_dataset in self.requests]

    def start_threads(self):
        for thread in self.threads_list:
            thread.start()

    def check_threads(self):
        for thread in self.threads_list:
            thread.join()


class PendingRequestYandex(Yandex):
    def __init__(self, request_dataset):

        self.request_id = request_dataset.id
        self.request_text = request_dataset.text
        self.xml_text = request_dataset.xml
        self.region_id = request_dataset.region_id

        self.site_list = list()
        self.concurency_object = object()
        self.order_on_page = 1

        self.parse_xml_text_with_bs4()
        self.get_site_list()
        self.clean_garbage()
        self.run_threads()

        self.make_concurency_object()
        if self.concurency_object.all_backlinks_collected:
            self.update_data_in_database()
            self.delete_request_from_queue()

    def make_site_object(self, site_dataset):
        PendingRequestSite(site_dataset)

    def make_concurency_object(self):
        self.concurency_object = PendingRequesConcurency(self.site_list, self.request_id)

    def update_data_in_database(self):
        sql = ("UPDATE concurent_site.main_request "
               f"SET backlinks_concurency = {self.concurency_object.site_backlinks_concurency}, "
               f"total_concurency = {self.concurency_object.site_total_concurency}, "
               f"average_total_backlinks = {self.concurency_object.average_total_backlinks}, "
               f"average_unique_backlinks = {self.concurency_object.average_unique_backlinks}, "
               f"status = 'ready';")

        pm.custom_request_to_database_without_return(sql)

    def delete_request_from_queue(self):
        sql = f"UPDATE concurent_site.main_handledxml SET status = 'conf' WHERE request_id = {self.request_id};"

        pm.custom_request_to_database_without_return(sql)

class PendingRequestSite(Site):
    def __init__(self, site_dataset):
        self.site_dataset = site_dataset

        self.url = str()
        self.html = str()

        self.get_url()
        self.get_site_type()
        self.get_domain()

        self.add_domain_data_to_dataset()


class PendingRequesConcurency(Concurency):
    def __init__(self, site_datasets, request_id):
        self.site_datasets = site_datasets
        self.request_id = request_id

        self.site_age_concurency = int()
        self.site_stem_concurency = int()
        self.site_volume_concurency = int()
        self.direct_upscale = int()
        self.all_backlinks_collected = True

        self.site_backlinks_concurency = int()
        self.site_total_concurency = int()

        self.check_all_backlinks_collected()

        if self.all_backlinks_collected:
            self.get_stat_weights()
            self.get_params_importance()
            self.get_concurency_data_from_database()
            self.calculate_site_backlinks_concurency()
            self.calculate_site_total_concurency()

    def check_all_backlinks_collected(self):
        unique_backlinks_total_count = 0
        total_backlinks_total_count = 0
        organic_sites_amount = 0

        for site_dataset in self.site_datasets:
            if site_dataset.type == 'organic':
                organic_sites_amount += 1

                if site_dataset.backlinks_status == 'complete':
                    unique_backlinks_total_count += site_dataset.unique_backlinks
                    total_backlinks_total_count += site_dataset.total_backlinks
                else:
                    self.all_backlinks_collected = False
                    break

        if self.all_backlinks_collected:
            self.average_unique_backlinks = unique_backlinks_total_count / organic_sites_amount
            self.average_total_backlinks = total_backlinks_total_count / organic_sites_amount

    def get_concurency_data_from_database(self):
        sql = ("SELECT age_concurency, stem_concurency, volume_concurency, direct_upscale "
               "FROM concurent_site.main_request "
               f"WHERE id = {self.request_id};")

        database_return = pm.custom_request_to_database_with_return(sql, 'one')

        self.site_age_concurency = database_return[0]
        self.site_stem_concurency = database_return[1]
        self.site_volume_concurency = database_return[2]
        self.direct_upscale = database_return[3]


if __name__ == '__main__':
    while True:
        Manager()
        print('Готово!')
        time.sleep(20)