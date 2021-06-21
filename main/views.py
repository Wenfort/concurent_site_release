from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.shortcuts import render, redirect

from .models import Request, RequestQueue, UserData, Order, Region
from django.contrib.auth.decorators import login_required
from main.tools.request_page_sorting import unmask_sort_type

from main.tools.xls_exporter import export_page

from microservices.conc_settings import REQUEST_COST

from main.user_logic.user_logic import SiteUser


def index(request):
    if request.user.is_authenticated:
        return redirect('/orders')
    else:
        return redirect('/authorization')


class ConfirmationData:
    def __init__(self, post_data):
        self.post_data = post_data
        self.raw_all_ordered_requests = post_data['requests_list']
        self.order_id = int()
        self.all_ordered_requests = list()
        self.requests_amount = int()
        self.bill = int()

        self.get_order_id()
        self.get_all_ordered_requests_list()
        self.calculate_bill()

    def get_order_id(self):
        try:
            self.order_id = int(self.post_data['order_id'])
        except:
            self.order_id = None

    def get_all_ordered_requests_list(self):
        self.all_ordered_requests = [request for request in self.raw_all_ordered_requests.split('\r\n') if request]
        self.requests_amount = len(self.all_ordered_requests)

    def calculate_bill(self):
        self.bill = self.requests_amount * REQUEST_COST


class OrderEngine:
    def __init__(self, user_data):
        self.user_id = user_data.id
        self.is_staff = user_data.account_data.is_staff
        self.all_requests_queryset = object()
        self.all_orders_queryset = object()
        self.sort_type = str()

    def get_all_user_orders(self):
        self.all_orders_queryset = Order.objects.filter(user_id=self.user_id)

    def _get_user_queryset(self, order_id):
        if order_id:
            return Request.objects.filter(order__user_order_id=order_id)
        else:
            return Request.objects.filter(order__user_id=self.user_id)

    def get_sorted_order_rows(self, request, order_id=0):
        """
        Сортировка на странице работает с помощью GET запроса. По умолчанию работает сортировка по уровню конкуренции в
            SEO. Названия альтернативных сортировок похожи на названия полей в БД, но все же отличаются от них.
            Это сделано в целях безопасности. Название сортировки приходит в GET запросе, отправляется в функцию
            unmask_sort_type, в ответ возвращается название поле в БД, по которому необходимо отсортировать данные.
        """
        self._get_all_user_requests_queryset(order_id)

        if 'sort' in request.GET:
            self.sort_type = request.GET['sort']
            unmasked_sort_type = unmask_sort_type(self.sort_type)
            self.all_requests_queryset = self.all_requests_queryset.select_related('region').order_by(
                unmasked_sort_type)
        else:
            self.all_requests_queryset = self.all_requests_queryset.select_related('region').order_by('seo_concurency')
            self.sort_type = 'seo_concurency'

    def _get_all_user_requests_queryset(self, order_id=0):
        if self.is_staff:
            self.all_requests_queryset = Request.objects.all()
        else:
            self.all_requests_queryset = self._get_user_queryset(order_id)

    @staticmethod
    def check_download_request(request):
        if 'download' in request.GET:
            return True

    def download_xls_file(self, user_data):
        buffer = export_page(self.all_requests_queryset, user_data.account_data.is_staff)
        return FileResponse(buffer, as_attachment=True, filename='report.xlsx')


class NewRequestHandler:
    def __init__(self, request, user_order_id=0):
        self.request_post_data = request.POST
        self.request = request
        self.request_account_data = request.user
        self.user_id = request.user.id
        self.user_order_id = user_order_id
        self.order_id = int()
        self.user_data = object
        self.requests_list = list()

        self.new_order = False
        self.is_money_enough = True

        self.get_user_data()
        self.make_requests_list()
        self.new_requests_amount = len(self.requests_list)

        if self.new_requests_amount > 0 and self.check_money_enough():
            if not user_order_id:
                self.new_order = True

            self.update_user_order_status()
            self.add_new_requests_to_database()

            self.update_user_balance()
        else:
            self.is_money_enough = False

    def get_user_data(self):
        self.user_data = SiteUser(self.request_account_data)

    def make_requests_list(self):
        requests_list = self.request_post_data['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.replace('\t', '')
        requests_list = requests_list.split('\n')
        self.requests_list = [request.lower() for request in requests_list if request]

    def add_new_requests_to_database(self):
        """
        Запрос одновременно добавляется в таблицы main_request и main_requestqueue.
        Запросами в этих таблицах занимаются разные микросервисы.
        """
        for request in self.requests_list:
            new_request = Request(text=request, region_id=self.user_data.region_id, order_id=self.order_id)
            new_request.save()
            new_request_id = new_request.pk
            RequestQueue(request_id=new_request_id, region_id=self.user_data.region_id).save()

    def get_latest_user_order(self, user_id):
        """
        У каждого пользователя собственная нумерация заказов. Начинается с 1. Для создания нового заказа
        необходимо получить номер предыдущего. Если заказ первый, то возвращается 0.
        """
        try:
            latest_user_order_id = Order.objects.latest('user_order_id').user_order_id
        except:
            latest_user_order_id = 0

        return latest_user_order_id

    def update_user_order_status(self):
        """
        Метод проверяет есть ли заказ с указанным ID.
        Если есть, то количество заказанных ключевых слов в заказе увеличивается на количество новых ключевых слов.
        Если нет, то вычисляется id последнего запроса заказа пользователя и создается новый заказ c id += 1.
        ID заказа пользователя хранится для того, чтобы в ЛК пользователь видел нумерацию заказов начиная с 1.
        """

        try:
            order = Order.objects.get(user_id=self.user_id, user_order_id=self.user_order_id)
            order.ordered_keywords_amount += self.new_requests_amount
            order.progress = 0
            order.save()
        except:
            latest_user_order_id = self.get_latest_user_order(self.user_id)

            order = Order(user_id=self.user_id, user_order_id=latest_user_order_id + 1,
                          ordered_keywords_amount=self.new_requests_amount)

            order.save()

        self.order_id = order.id

    def update_user_balance(self):
        """
        Если пользователь создал новый заказ, то счетчик заказов увеличивается. Иначе, увеличивается только кол-во
        заказанных ключевых слов.
        """
        user = UserData.objects.filter(user_id=self.user_id)
        if self.new_order:
            user.update(balance=self.user_data.balance - self.new_requests_amount * REQUEST_COST,
                        orders_amount=self.user_data.orders + 1,
                        ordered_keywords=self.user_data.ordered_keywords + self.new_requests_amount,
                        )
        else:
            user.update(balance=self.user_data.balance - self.new_requests_amount * REQUEST_COST,
                        ordered_keywords=self.user_data.ordered_keywords + self.new_requests_amount,
                        )

    def check_money_enough(self):
        if self.new_requests_amount * REQUEST_COST <= self.user_data.balance:
            return True


def render_page_with_privilegies(request, context):
    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


@login_required
def results(request):
    """
    Метод отображает абсолютно все заказанные пользователем ключевые слова.
    Если страницу просматривает админ, показываются абсолютно все заказанные ключевые слова всех пользователей.
    Если пришел запрос на загрузку xls файла, метод обрабатывает только его.
    """
    user_data = SiteUser(request.user)
    order_engine = OrderEngine(user_data)

    if order_engine.check_download_request(request):
        return order_engine.download_xls_file(user_data)

    order_engine.get_sorted_order_rows(request)

    all_regions = Region.objects.all().order_by('name')

    context = {'all_requests': order_engine.all_requests_queryset,
               'sort_type': order_engine.sort_type,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'region': user_data.region_name,
               'balance': user_data.balance,
               'regions': all_regions,
               }

    return render_page_with_privilegies(request, context)


@login_required
def requests_from_order(request, order_id):
    """
    Отображает все ключевые слова в рамках заказа.
    """
    user_data = SiteUser(request.user)
    order_engine = OrderEngine(user_data)

    order_engine.get_sorted_order_rows(request, order_id)

    if not order_engine.all_requests_queryset:
        return HttpResponseNotFound('Страница не найдена')

    if order_engine.check_download_request(request):
        return order_engine.download_xls_file(user_data)

    all_regions = Region.objects.all().order_by('name')

    context = {'all_requests': order_engine.all_requests_queryset,
               'sort_type': order_engine.sort_type,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'region': user_data.region_name,
               'balance': user_data.balance,
               'regions': all_regions,
               }

    return render_page_with_privilegies(request, context)


@login_required
def get_orders_page(request):
    """
    Отображает все заказы пользователя
    """
    user_data = SiteUser(request.user)
    order_engine = OrderEngine(user_data)
    order_engine.get_all_user_orders()

    all_regions = Region.objects.all().order_by('name')

    context = {'all_orders_list': order_engine.all_orders_queryset,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'regions': all_regions,
               'region': user_data.region_name
               }

    return render(request, 'main/orders.html', context)


@login_required
def user_confirmation(request):
    user_data = SiteUser(request.user)
    confirmation_data = ConfirmationData(request.POST)

    context = {
        'requests_list': confirmation_data.all_ordered_requests,
        'requests_list_without_format': confirmation_data.raw_all_ordered_requests,
        'previous_page': confirmation_data.post_data['previous_page'],
        'requests_amount': confirmation_data.requests_amount,
        'funds': confirmation_data.bill,
        'order_id': confirmation_data.order_id,
        'user_data': user_data,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance,
        'geo': user_data.region_name,
    }

    return render(request, 'main/user_confirmation.html', context)


def get_id_from_post_data(post_data):
    try:
        order_id = int(post_data['order_id'])
    except:
        order_id = None

    return order_id


@login_required
def handle_new_request(request):
    if request.method == "POST":
        order_id = get_id_from_post_data(request.POST)

        request_handler = NewRequestHandler(request, order_id)
        if request_handler.check_money_enough():
            previous_page = request.POST['previous_page']

            return HttpResponseRedirect(previous_page)
        else:
            return HttpResponse(
                f'К сожалению, на балансе недостаточно средств. Нужно пополнить еще на '
                f'{request_handler.new_requests_amount * REQUEST_COST - request_handler.user_data.balance} рублей')
