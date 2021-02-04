from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect

from .models import Request, RequestQueue, UserData, Order

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


        self.get_user_data()
        self.get_user_id()
        self.get_user_balance()
        self.get_all_user_order_rows()
        self.get_unique_user_order_rows()
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


def results(request):
    all_requests_list = get_list_or_404(Request.objects.order_by('site_seo_concurency'))
    user_data = User(request.user.username)

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


def add_new_requests_to_queue(request):
    if request.method == "POST":

        user_data = User(request.user.username)

        requests_list = request.POST['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.split('\n')
        for req in requests_list:
            if Request.objects.filter(request=req):
                pass
            else:
                RequestQueue(request=req).save()
                Request(request=req).save()

        order_id = Order.objects.latest('pk').id + 1

        new_requests = Request.objects.filter(request__in=requests_list)
        new_requests_amount = len(new_requests)
        for new_request in new_requests:
            Order(request_id=new_request.id,
                  user_id=user_data.id,
                  order_id=order_id
                  ).save()

        UserData(id=user_data.id,
                 balance=user_data.balance - new_requests_amount,
                 name=user_data.name,
                 ).save()

        return HttpResponseRedirect('/main/results')
    else:
        form = NewRequest()
        return render(request, 'main/add_to_queue.html', {'form': form})


def get_orders_page(request):
    user_data = User(request.user.username)

    form = NewRequest()
    context = {'all_orders_list': user_data.unique_order_rows,
               'orders': user_data.orders_amount,
               'keywords_ordered': user_data.ordered_keywords_amount,
               'balance': user_data.balance,
               'form': form}

    return render(request, 'main/orders.html', context)


def balance(request):
    pass


def ordered_requests(request):
    pass
