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
        self.user_orders = int
        self.user_ordered_keywords = int

        self.get_user_data()
        self.get_user_id()
        self.get_user_balance()
        self.get_user_orders()
        self.get_user_ordered_requests()

    def get_user_data(self):
        self.user = UserData.objects.get(name=self.name)

    def get_user_id(self):
        self.id = self.user.id

    def get_user_balance(self):
        self.balance = self.user.balance

    def get_user_orders(self):
        self.user_orders = self.user.orders_amount

    def get_user_ordered_requests(self):
        self.user_ordered_keywords = self.user.ordered_keywords

class Orders:
    def __init__(self, user_id):
        self.user_id = user_id
        self.all_order_rows = object
        self.unique_order_rows = object

        self.get_all_user_order_rows()
        self.get_unique_user_order_rows()

    def get_all_user_order_rows(self):
        self.all_order_rows = Order.objects.filter(user_id=self.user_id)

    def get_unique_user_order_rows(self):
        self.unique_order_rows = OrderStatus.objects.filter(user_id=self.user_id)

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
        OrderStatus(order_id=self.order_id, user_id=self.user_data.id,
                    ordered_keywords_amount=self.new_requests_amount).save()

    def update_user_balance(self):
        UserData(id=self.user_data.id,
                 balance=self.user_data.balance - self.new_requests_amount,
                 name=self.user_data.name,
                 orders_amount=self.user_data.user_orders + 1,
                 ordered_keywords=self.user_data.user_ordered_keywords + self.new_requests_amount,
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
                       'orders': user_data.user_orders,
                       'keywords_ordered': user_data.user_ordered_keywords,
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
        orders_data = Orders(user_data.id)
        form = NewRequest()

        context = {'all_orders_list': orders_data.unique_order_rows,
                   'orders': user_data.user_orders,
                   'keywords_ordered': user_data.user_ordered_keywords,
                   'balance': user_data.balance,
                   'form': form}

        return render(request, 'main/orders.html', context)


def requests_from_order(request, order_id):
    user_data = User(request.user.username)
    order_data = Order.objects.filter(order_id=order_id)

    requests_ids = [od.request_id for od in order_data]
    all_requests_list = Request.objects.filter(id__in=requests_ids)


    context = {'all_requests_list': all_requests_list,
               'orders': user_data.user_orders,
               'keywords_ordered': user_data.user_ordered_keywords,
               'balance': user_data.balance}

    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


def balance(request):
    pass
