from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect
from .models import Request, RequestQueue, UserData, Order, Region
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from main.tools.xls_exporter import export_page

from microservices.conc_settings import REQUEST_COST

from main.user_logic.user_logic import SiteUser


def index(request):
    if request.user.is_authenticated:
        return redirect('/orders')
    else:
        return redirect('/authorization')


class Orders:
    def __init__(self, user_data):
        self.user_id = user_data.id
        self.is_staff = user_data.account_data.is_staff

    def get_all_user_orders(self):
        return Order.objects.filter(user_id=self.user_id)

    def get_admin_queryset(self):
        return Request.objects.all()

    def get_user_queryset(self, order_id):
        if order_id:
            return Request.objects.filter(order__user_order_id=order_id)
        else:
            return Request.objects.filter(order__user_id=self.user_id)

    def get_all_user_order_rows(self, order_id=0):

        if self.is_staff:
            return self.get_admin_queryset()
        else:
            return self.get_user_queryset(order_id)


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
        self.money_is_enough = True

        self.get_user_data()
        self.make_requests_list()
        self.new_requests_amount = len(self.requests_list)

        if self.new_requests_amount > 0 and self.is_money_enough():
            if not user_order_id:
                self.new_order = True

            self.update_user_order_status()
            self.add_new_requests_to_database()

            self.update_user_balance()
        else:
            self.money_is_enough = False

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
            order.status = 0
            order.save()
        except:
            latest_user_order_id = self.get_latest_user_order(self.user_id)

            order = Order(user_id=self.user_id, user_order_id=latest_user_order_id + 1,
                          ordered_keywords_amount=self.new_requests_amount)

            order.save()

        self.order_id = order.id

    def update_user_balance(self):
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

    def is_money_enough(self):
        if self.new_requests_amount * REQUEST_COST <= self.user_data.balance:
            return True


def unmask_sort_type(masked_sort_type):
    """Прячет от пользователя реальное название row в таблице БД"""
    unmasked_sort_type = str()
    if 'request' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('request', 'request_text')
    elif 'age' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('age', 'age_concurency')
    elif 'stem' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('stem', 'stem_concurency')
    elif 'volume' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('volume', 'volume_concurency')
    elif 'backlinks' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('backlinks', 'backlinks_concurency')
    elif 'seo' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('seo', 'seo_concurency')
    elif 'direct' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('direct', 'direct_upscale')
    elif 'total' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('total', 'total_concurency')
    elif 'region' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('region', 'region_id')
    elif 'amount' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('amount', 'request_views')
    elif 'vital_count' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('vital_count', 'vital_sites_count')
    elif 'avg_backs' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_backs', 'average_total_backlinks')
    elif 'avg_unique_backs' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_unique_backs', 'average_unique_backlinks')
    elif 'avg_vol' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_vol', 'average_volume')
    elif 'avg_old' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_old', 'average_age')

    return unmasked_sort_type


def check_download_request(request):
    if 'download' in request.GET:
        return True


def download_xls_file(all_requests, user_data):
    buffer = export_page(all_requests, user_data.account_data.is_staff)
    return FileResponse(buffer, as_attachment=True, filename='report.xlsx')

def render_page_with_privilegies(request, context):
    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


def get_sorted_order_rows(request, all_user_order_rows):
    if 'sort' in request.GET:
        sort_type = request.GET['sort']
        unmasked_sort_type = unmask_sort_type(sort_type)
        all_user_order_rows = all_user_order_rows.select_related('region').order_by(unmasked_sort_type)
    else:
        all_user_order_rows = all_user_order_rows.select_related('region').order_by('seo_concurency')
        sort_type = 'seo_concurency'

    return all_user_order_rows, sort_type

@login_required
def results(request):
    """
    Отображает абсолютно все заказанные пользователем ключевые слова.
    Если страницу просматривает админ, показываются абсолютно все заказанные ключевые слова всех пользователей.
    """
    user_data = SiteUser(request.user)
    all_regions = Region.objects.all().order_by('name')
    all_requests = Orders(user_data).get_all_user_order_rows()

    if check_download_request(request):
        return download_xls_file(all_requests, user_data)

    all_requests, sort_type = get_sorted_order_rows(request, all_requests)

    context = {'all_requests': all_requests,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'regions': all_regions,
               'region': user_data.region,
               'sort_type': sort_type,
               }

    return render_page_with_privilegies(request, context)


@login_required
def requests_from_order(request, order_id=0):
    """
    Отображает все ключевые слова в рамках заказа
    """
    user_data = SiteUser(request.user)
    all_requests = Orders(user_data).get_all_user_order_rows(order_id)
    all_regions = Region.objects.all().order_by('name')
    all_requests, sort_type = get_sorted_order_rows(request, all_requests)

    if check_download_request(request):
        return download_xls_file(all_requests, user_data)

    context = {'all_requests': all_requests,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'order_id': order_id,
               'regions': all_regions,
               'region': user_data.region,
               'sort_type': sort_type,
               }

    return render_page_with_privilegies(request, context)


@login_required
def get_orders_page(request):
    """
    Отображает все заказы пользователя
    """
    user_data = SiteUser(request.user)
    all_user_orders = Orders(user_data).get_all_user_orders()
    all_regions = Region.objects.all().order_by('name')

    context = {'all_orders_list': all_user_orders,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'regions': all_regions,
               'region': user_data.region
               }

    return render(request, 'main/orders.html', context)

def user_confirmation(request):
    user_data = SiteUser(request.user)

    try:
        order_id = int(request.POST['order_id'])
    except:
        order_id = None

    post_data = request.POST
    requests_list_without_format = post_data['requests_list']
    requests_list = requests_list_without_format.split('\r\n')
    requests_amount = len(requests_list)
    bill = requests_amount * REQUEST_COST
    context = {
        'user_data': user_data,
        'requests_list': requests_list,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance,
        'requests_list_without_format': requests_list_without_format,
        'previous_page': post_data['previous_page'],
        'geo': post_data['geo'],
        'requests_amount': requests_amount,
        'funds': bill,
        'order_id': order_id,
    }
    return render(request, 'main/user_confirmation.html', context)


def handle_new_request(request):
    if request.method == "POST":
        try:
            order_id = int(request.POST['order_id'])
        except:
            order_id = None

        request_handler = NewRequestHandler(request, order_id)
        if request_handler.is_money_enough():
            previous_page = request.POST['previous_page']

            return HttpResponseRedirect(previous_page)
        else:
            return HttpResponse(
                f'К сожалению, на балансе недостаточно средств. Нужно пополнить еще на '
                f'{request_handler.new_requests_amount * REQUEST_COST - request_handler.user_data.balance} рублей')
