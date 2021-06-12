from microservices import postgres_mode as pm
import time
from microservices.microservices_dataclasses import OrderDataSet


class OrderStatusHandler:
    def __init__(self):
        self.order_datasets = list()

        self.make_order_datasets()
        self.update_orders_status()

    def update_orders_status(self):
        """
        Если метод обнаруживает, что актуальный процент выполнения запроса выше, чем сохраненный в БД, вызывает
            метод перезаписи данных.
        """
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
        """
        Метод берет из БД заказы, чей прогресс выполнения меньше 100%. Внутри запроса сразу подготавливает процент
            выполнения для каждого заказа.
        Комментарии к запросу:
            comletition_percent - актуальный процент выполнения заказа пользователя. Для его получения необходимо
                посчитать количество запросов со статусом 'ready', разделить на ordered_keywords_amount из таблцы ord и
                умножить на 100.
            progress - процент выполнения заказа пользователя, который уже сохранен в ДБ. Хранится в столбце progress
                таблицы ord
        """
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