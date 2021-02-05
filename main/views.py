from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect

from .models import Request, RequestQueue, UserData, Order, OrderStatus

from .forms import NewRequest


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class User:
    def __init__(self, name):
        self.name = name
        self.user = object
        self.id = int
        self.balance = int
        self.all_order_rows = object
        self.unique_order_rows = object
        self.ordered_keywords_amount = int
        self.orders_amount = int
        self.super_orders = list

        self.get_user_data()
        self.get_user_id()
        self.get_user_balance()
        self.get_all_user_order_rows()
        self.get_unique_user_order_rows()
        self.check_order_status()
        self.calculate_user_statistic()

    def get_user_data(self):
        self.user = UserData.objects.get(name=self.name)

    def get_user_id(self):
        self.id = self.user.id

    def get_user_balance(self):
        self.balance = self.user.balance

    def get_all_user_order_rows(self):
        self.all_order_rows = Order.objects.filter(user_id=self.id)

    def get_unique_user_order_rows(self):
        self.unique_order_rows = self.all_order_rows.distinct('order_id')

    def calculate_user_statistic(self):
        self.ordered_keywords_amount = len(self.all_order_rows)
        self.orders_amount = len(self.unique_order_rows)

    def check_order_status(self):
        orders_to_check = list()
        for unique_order_row in self.unique_order_rows:
            orders_to_check.append(str(unique_order_row.order_id))

        self.super_orders = OrderStatus.objects.filter(order_id__in=orders_to_check)

class NewRequestHandler:
    def __init__(self, request):
        self.request = request.POST
        self.user_name = request.user.username
        self.user_data = object
        self.requests_list = list()
        self.order_id = int()
        self.new_requests = list()
        self.new_requests_amount = int()

        self.get_user_data()
        self.make_requests_list()
        self.add_new_requests_to_database()
        self.get_order_id()
        self.get_new_requests_id()
        self.calculate_new_requests_amount()
        self.update_user_orders()
        self.update_user_order_status()
        self.update_user_balance()

    def get_user_data(self):
        self.user_data = User(self.user_name)

    def make_requests_list(self):
        requests_list = self.request['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.split('\n')
        self.requests_list = requests_list

    def add_new_requests_to_database(self):
        for request in self.requests_list:
            if Request.objects.filter(request=request):
                pass
            else:
                RequestQueue(request=request).save()
                Request(request=request).save()

    def get_order_id(self):
        try:
            self.order_id = Order.objects.latest('pk').id + 1
        except:
            self.order_id = 1

    def get_new_requests_id(self):
        self.new_requests = Request.objects.filter(request__in=self.requests_list)

    def calculate_new_requests_amount(self):
        self.new_requests_amount = len(self.new_requests)

    def update_user_orders(self):
        for new_request in self.new_requests:
            Order(request_id=new_request.id,
                  user_id=self.user_data.id,
                  order_id=self.order_id
                  ).save()

    def update_user_order_status(self):
        OrderStatus(order_id=self.order_id, user_id=self.user_data.id).save()

    def update_user_balance(self):
        UserData(id=self.user_data.id,
                 balance=self.user_data.balance - self.new_requests_amount,
                 name=self.user_data.name,
                 ).save()

def results(request):

    if request.method == "POST":
        NewRequestHandler(request)
        return HttpResponseRedirect('/main/results')
    else:
        user_data = User(request.user.username)
        all_requests_list = get_list_or_404(Request.objects.order_by('site_seo_concurency'))
        try:
            context = {'all_requests_list': all_requests_list,
                       'orders': user_data.orders_amount,
                       'keywords_ordered': user_data.ordered_keywords_amount,
                       'balance': user_data.balance}
        except:
            context = {'all_requests_list': all_requests_list}
        if request.user.is_staff:
            return render(request, 'main/restricted_requests.html', context)
        else:
            return render(request, 'main/non_restricted_requests.html', context)


def get_orders_page(request):
    if request.method == "POST":
        NewRequestHandler(request)
        return HttpResponseRedirect('/main/orders')
    else:
        user_data = User(request.user.username)
        form = NewRequest()

        context = {'all_orders_list': user_data.super_orders,
                   'orders': user_data.orders_amount,
                   'keywords_ordered': user_data.ordered_keywords_amount,
                   'balance': user_data.balance,
                   'form': form}

        return render(request, 'main/orders.html', context)

def requests_from_order(request, order_id):
    a = 'b'
    return HttpResponseRedirect('/main/orders')

def balance(request):
    pass