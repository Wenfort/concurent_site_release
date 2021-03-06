from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect
from .models import Request, RequestQueue, UserData, Order, OrderStatus, Region
from django.contrib.auth.decorators import login_required


from .forms import NewRequest
from xls_test import export_page

from conc_settings import REQUEST_COST


def index(request):
    if request.user.is_authenticated:
        return redirect('/orders')
    else:
        return redirect('/authorization')


class SiteUser:
    def __init__(self, user_id):
        self.id = user_id
        self.user = object
        self.user_role = str
        self.balance = int
        self.orders = int
        self.ordered_keywords = int
        self.region_id = int
        self.region = str

        self.get_data()
        self.get_user_role()
        self.get_balance()
        self.get_orders()
        self.get_ordered_requests()
        self.get_region()


    def get_data(self):
        self.user = UserData.objects.get(user_id=self.id)

    def get_user_role(self):
        if self.user.user.is_staff:
            self.user_role = 'admin'
        else:
            self.user_role = 'user'

    def get_balance(self):
        self.balance = self.user.balance

    def get_orders(self):
        self.orders = self.user.orders_amount

    def get_ordered_requests(self):
        self.ordered_keywords = self.user.ordered_keywords

    def get_region(self):
        self.region_id = self.user.region_id
        self.region = Region.objects.get(region_id=self.region_id).name


class Orders:
    def __init__(self, user_id):
        self.user_id = user_id
        self.all_order_rows = list
        self.unique_order_rows = list

        self.get_all_user_order_rows()
        self.get_unique_user_order_rows()


    def get_all_user_order_rows(self):
        self.all_order_rows = Order.objects.filter(user_id=self.user_id)

    def get_unique_user_order_rows(self):
        self.unique_order_rows = OrderStatus.objects.filter(user_id=self.user_id).order_by('-user_order_id')

    def all_ordered_requests(self):
        ordered_requests_ids = [order.request_id for order in self.all_order_rows]
        return Request.objects.filter(request_id__in=ordered_requests_ids).order_by('-site_seo_concurency')

    def all_requests_from_order(self, user_order_id):
        order_id = self.unique_order_rows.get(user_order_id=user_order_id).order_id
        ordered_requests_ids = [order.request_id for order in self.all_order_rows.filter(order_id=order_id)]
        return Request.objects.filter(request_id__in=ordered_requests_ids)


class NewRequestHandler:
    def __init__(self, request, user_order_id=0):
        self.request = request.POST
        self.user_id = request.user.id
        self.user_order_id = user_order_id
        self.order_id = int()
        self.user_data = object
        self.requests_list = list()

        self.new_requests = list()
        self.new_order = False
        self.money_is_enough = True
        self.new_requests_amount = int()

        self.get_user_data()
        self.make_requests_list()
        self.add_new_requests_to_database()

        self.calculate_new_requests_amount()

        if self.is_money_enough():
            if self.new_requests_amount > 0:
                if not user_order_id:
                    self.new_order = True

                self.update_user_order_status()
                self.update_user_orders()

                self.update_user_balance()
        else:
            self.money_is_enough = False

    def get_user_data(self):
        self.user_data = SiteUser(self.user_id)

    def make_requests_list(self):
        requests_list = self.request['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.replace('\t', '')
        requests_list = requests_list.split('\n')
        self.requests_list = [request.lower() for request in requests_list if request]

    def add_new_requests_to_database(self):
        for request in self.requests_list:
            try:
                new_request = Request.objects.get(request_text=request, region_id=self.user_data.region_id)
            except:
                new_request = Request(request_text=request, region_id=self.user_data.region_id)
                RequestQueue(request_text=request, geo=self.user_data.region_id).save()
                new_request.save()
                new_request_id = new_request.pk

                self.new_requests.append(new_request_id)

    def calculate_new_requests_amount(self):
        self.new_requests_amount = len(self.new_requests)

    def update_user_orders(self):
        for new_request in self.new_requests:
            Order(request_id=new_request,
                  user_id=self.user_id,
                  order_id=self.order_id
                  ).save()

    def update_user_order_status(self):
        all_user_orders = OrderStatus.objects.filter(user_id=self.user_id)
        order = all_user_orders.filter(user_order_id=self.user_order_id)
        if order:
            ordered_requests_amount = order[0].ordered_keywords_amount
            if self.new_order:
                order.update(ordered_keywords_amount=ordered_requests_amount + self.new_requests_amount)
            else:
                order.update(ordered_keywords_amount=ordered_requests_amount + self.new_requests_amount, status=0)
            self.order_id = order[0].order_id
        else:
            try:
                latest_user_order_id = all_user_orders.latest('user_order_id').user_order_id
            except:
                latest_user_order_id = 0

            order = OrderStatus(user_id=self.user_id,
                        user_order_id=latest_user_order_id + 1,
                        ordered_keywords_amount=self.new_requests_amount)
            order.save()
            self.order_id = order.order_id


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
        if self.new_requests_amount <= self.user_data.balance:
            return True


def unmask_sort_type(masked_sort_type):
    """Прячет от пользователя реальное название row в таблице БД"""
    unmasked_sort_type = str
    if 'request' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('request', 'request_text')
    elif 'age' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('age', 'site_age_concurency')
    elif 'stem' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('stem', 'site_stem_concurency')
    elif 'volume' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('volume', 'site_volume_concurency')
    elif 'backlinks' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('backlinks', 'site_backlinks_concurency')
    elif 'seo' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('seo', 'site_seo_concurency')
    elif 'direct' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('direct','direct_upscale')
    elif 'total' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('total', 'site_total_concurency')
    elif 'region' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('region', 'region_id')
    elif 'amount' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('amount', 'request_views')

    return unmasked_sort_type


@login_required
def get_orders_page(request):
    user_data = SiteUser(request.user.id)
    orders_data = Orders(user_data.id)
    all_regions = Region.objects.all().order_by('name')
    form = NewRequest()

    context = {'all_orders_list': orders_data.unique_order_rows,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'form': form,
               'regions': all_regions,
               'region': user_data.region
               }

    return render(request, 'main/orders.html', context)


@login_required
def results(request):
    user_data = SiteUser(request.user.id)
    all_regions = Region.objects.all().order_by('name')

    if request.user.is_staff:
        all_requests = Request.objects.all()
    else:
        orders_data = Orders(user_data.id)
        all_requests = orders_data.all_ordered_requests().select_related('region')

    try:
        prepare_report = request.GET['download']
        if prepare_report == 'True':
            buffer = export_page(all_requests, user_data.user_role)
            return FileResponse(buffer, as_attachment=True, filename='report.xlsx')
    except:
        pass


    try:
        sort_type = request.GET['sort']
        unmasked_sort_type = unmask_sort_type(sort_type)
        all_requests = all_requests.order_by(unmasked_sort_type)
    except:
        sort_type = None
        all_requests = all_requests.order_by('-site_seo_concurency')

    context = {'all_requests': all_requests,
               'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance,
               'regions': all_regions,
               'region': user_data.region,
               'sort_type': sort_type,
               }

    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


@login_required
def requests_from_order(request, order_id):
    user_data = SiteUser(request.user.id)
    order_data = Orders(user_data.id)
    all_regions = Region.objects.all().order_by('name')
    try:
        sort_type = request.GET['sort']
        unmasked_sort_type = unmask_sort_type(sort_type)
        all_requests = order_data.all_requests_from_order(order_id).select_related('region').order_by(unmasked_sort_type)
    except:
        sort_type = None
        all_requests = order_data.all_requests_from_order(order_id).select_related('region').order_by('-site_seo_concurency')

    try:
        prepare_report = request.GET['download']
        if prepare_report == 'True':
            buffer = export_page(all_requests, user_data.user_role)
            return FileResponse(buffer, as_attachment=True, filename='report.xlsx')

    except:
        pass

    if all_requests:
        context = {'all_requests': all_requests,
                   'orders': user_data.orders,
                   'keywords_ordered': user_data.ordered_keywords,
                   'balance': user_data.balance,
                   'order_id': order_id,
                   'regions': all_regions,
                   'region': user_data.region,
                   'sort_type': sort_type,
                   }

        if request.user.is_staff:
            return render(request, 'main/restricted_requests.html', context)
        else:
            return render(request, 'main/non_restricted_requests.html', context)
    else:
        return HttpResponse('У вас нет доступа к этой странице')


def user_confirmation(request):
    try:
        order_id = int(request.POST['order_id'])
    except:
        order_id = None

    post_data = request.POST
    requests_list_without_format = post_data['requests_list']
    requests_list = requests_list_without_format.split('\r\n')
    requests_amount = len(requests_list)
    funds = requests_amount * REQUEST_COST
    context = {
        'requests_list': requests_list,
        'requests_list_without_format': requests_list_without_format,
        'previous_page': post_data['previous_page'],
        'geo': post_data['geo'],
        'requests_amount': requests_amount,
        'funds': funds,
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
                f'К сожалению, на балансе недостаточно средств. Нужно пополнить еще на {request_handler.new_requests_amount * REQUEST_COST - request_handler.user_data.balance} рублей')
