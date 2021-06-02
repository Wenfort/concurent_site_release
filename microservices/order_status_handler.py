from microservices import postgres_mode as pm
from dataclasses import dataclass
import time


@dataclass
class OrderDataSet:
    id: int
    actual_completition_percent: int
    stored_completition_percent: int


class OrderStatusHandler:
    def __init__(self):
        self.order_datasets = list()

        self.make_order_datasets()
        self.update_orders_status()

    def update_orders_status(self):
        for order_dataset in self.order_datasets:
            if order_dataset.actual_completition_percent > order_dataset.stored_completition_percent:
                self._update_completition_percent(order_dataset)

    def _update_completition_percent(self, order_dataset):
        sql = ("UPDATE concurent_site.main_order SET "
               f"progress = {order_dataset.actual_completition_percent} "
               f"WHERE id ={order_dataset.id};")

        pm.custom_request_to_database_without_return(sql)

    def make_order_datasets(self):
        not_completed_orders_data = self._get_not_completed_orders_data()

        self.order_datasets = [OrderDataSet(id=order[0], actual_completition_percent=order[1],
                                            stored_completition_percent=order[2])
                               for order in not_completed_orders_data]


    def _get_not_completed_orders_data(self):
        sql = """
                SELECT order_id,
                       ceil(cast(COUNT(*) as decimal) / MAX(ordered_keywords_amount) * 100) as comletition_percent,
                       MAX(progress) AS progress
                FROM concurent_site.main_request req
                INNER JOIN
                    concurent_site.main_order ord ON (req.order_id = ord.id)
                WHERE order_id IN
                      (SELECT id FROM concurent_site.main_order WHERE main_order.progress < 100) AND
                      req.status = 'ready'
                GROUP BY order_id;
              """

        database_return = pm.custom_request_to_database_with_return(sql)
        return database_return

while True:
    OrderStatusHandler()
    time.sleep(60)