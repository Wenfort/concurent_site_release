Структура проекта:
[Структура базы данных](https://lucid.app/lucidchart/45eb7003-c18a-48f7-869d-0dfeba193875/view)
[Алгоритм работы сервиса](https://lucid.app/lucidchart/7cc211e6-9874-4500-9600-8f8a0f56a47e/view)
[Схема взаимодействия классов и баз данных](https://lucid.app/lucidchart/028b9ac8-d755-423e-8b02-049f92f29e32/view)

Краткое описание:

Проект состоит из 5 отдельных микросервисов, которые общаются друг с другом с помощью базы данных.

+ xml_handler.py
  + Берет запросы из очереди в БД
  + Опрашивает сторонний сервис по API и получает поисковую выдачу Yandex в формате XML
  + Если данные выглядят подозрительно, отправляет запрос на перепроверку
  + Обновляет данные в БД, записывая туда сам XML ответ для последующей обработки другими сервисами и ключевые показатели поисковой выдачи
+ new_requests_handler.py
  + Получает XML поисковой выдачи из БД. Количество XML ограничено кол-вом ядер процессора.  
  + Для каждого XML создает отдельный процесс, который получает информацию о контенте, возрасте, бэклинках и других данных о сайте.
  + Подсчитывает все полученные данные, применяет разные веса к характеристикам
  + Валидирует данные
  + Если данные валидны - сохраняет все данные в БД
  + Если нет - ставит в очередь на перепроверку
+ pending_backlinks_handler.py
  + Главная причина по которой данные в new_requests_handler признаются не валидными - внешний API сервис отдал не всю информацию по бэклинкам. У него есть собственная очередь запросов, в которой можно провести несколько десятков минут. Нет смысла ждать заставлять пользователя ждать, лучше просто периодически опрашивать сервис о состоянии запроса в очереди.
  + Этим и занимается pending_requests_handler
  + Как только ответ от внешнего сервиса по домену получен, данные в БД обновляются
+ pending_requests_handler.py
  + Сервис получает из БД запросы пользователей, данные о которых new_requests_handler признал не валидными. 
  + Проверяет достаточно ли данных о бэклинках сайтов в выдаче, чтобы признать данные валидными
  + Если достаточно - считает уровень конкуренции по бэклинкам и обновляет итоговую статистику и результат
  + Если недостаточно - возвращается к запросу позже
+ order_status_handler.py
  + С определенным интервалом проверяет актуальный процент выполнения заказов пользователей
