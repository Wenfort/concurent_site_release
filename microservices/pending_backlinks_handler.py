from microservices import postgres_mode as pm
import time
from microservices.new_requests_handler import Backlinks


class BacklinksHandler(Backlinks):
    def __init__(self):
        self.token = str()
        self.status = str()
        self.unique_backlinks = int()
        self.total_backlinks = int()
        self.backlinks_status = str()
        self.domain_group = 0

        self.get_token()
        for domain in self.get_pending_domains():
            if self.have_new_backlinks_data(domain):
                self.update_database()

    def get_pending_domains(self):
        sql = "SELECT name FROM concurent_site.main_domain WHERE status = 'pending'"
        database_return = pm.custom_request_to_database_with_return(sql)
        pending_domains = [domain[0] for domain in database_return]
        return pending_domains

    def have_new_backlinks_data(self, domain):
        request_json = self._get_backlinks_service_json_answer(domain)
        if request_json['success']:
            self.unique_backlinks = int(request_json["summary"]["mjDin"])
            self.total_backlinks = int(request_json["summary"]["mjHin"])
            self.backlinks_status = 'complete'

            if self.unique_backlinks >= 10000 or self.total_backlinks >= 30000:
                self.domain_group = 1

            return True

    def update_database(self):
        sql = ("UPDATE concurent_site.main_domain SET "
               f"unique_backlinks = {self.unique_backlinks}, "
               f"total_backlinks = {self.total_backlinks}, "
               f"status = '{self.backlinks_status}', "
               f"domain_group = {self.domain_group}")

        pm.custom_request_to_database_without_return(sql)

while True:
    BacklinksHandler()
    print('Готово!')
    time.sleep(30)
