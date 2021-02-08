from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect
from django.contrib.auth import authenticate, login, logout as django_logout
from django.utils import timezone
from .models import Request, RequestQueue, UserData, Order, OrderStatus, TicketPost, Ticket
from django.contrib.auth.models import User

from .forms import NewRequest, NewUser, AuthUser


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class SiteUser:
    def __init__(self, name):
        self.name = name
        self.user = object
        self.user_role = str
        self.id = int
        self.balance = int
        self.orders = int
        self.ordered_keywords = int

        self.get_data()
        self.get_user_role()
        self.get_id()
        self.get_balance()
        self.get_orders()
        self.get_ordered_requests()

    def get_data(self):
        self.user = UserData.objects.get(name=self.name)

    def get_user_role(self):
        if self.name == 'airlove':
            self.user_role = 'admin'
        else:
            self.user_role = 'user'

    def get_id(self):
        self.id = self.user.id

    def get_balance(self):
        self.balance = self.user.balance

    def get_orders(self):
        self.orders = self.user.orders_amount

    def get_ordered_requests(self):
        self.ordered_keywords = self.user.ordered_keywords


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
        self.user_data = SiteUser(self.user_name)

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
        OrderStatus(order_id=self.order_id,
                    user_id=self.user_data.id,
                    ordered_keywords_amount=self.new_requests_amount).save()

    def update_user_balance(self):
        UserData(id=self.user_data.id,
                 balance=self.user_data.balance - self.new_requests_amount,
                 name=self.user_data.name,
                 orders_amount=self.user_data.orders + 1,
                 ordered_keywords=self.user_data.ordered_keywords + self.new_requests_amount,
                 ).save()


class NewUserHandler:
    def __init__(self, request):
        self.request = request.POST
        self.user_name = str
        self.password = str
        self.password_again = str
        self.email = str
        self.valid = False


        self.get_user_name()
        self.get_user_password()
        self.get_user_email()

        if self.compare_passwords():
            self.valid = True
            self.create_user()

    def get_user_name(self):
        self.user_name = self.request['username']

    def get_user_password(self):
        self.password = self.request['password']
        self.password_again = self.request['password_again']

    def get_user_email(self):
        self.email = self.request['email']

    def create_user(self):
        User.objects.create_user(self.user_name, self.email, self.password)
        UserData(name=self.user_name, balance=50).save()

    def compare_passwords(self):
        return self.password == self.password_again


class Tickets:

    def __init__(self, user):
        self.user_name = user.name
        self.user_role = user.user_role
        self.all_tickets = object


    def get_all_user_tickets(self):
        self.all_tickets = Ticket.objects.filter(author=self.user_name).order_by('-id')
        return self.all_tickets

    def get_all_admin_tickets(self):
        self.all_tickets = Ticket.objects.all().order_by('-id')
        return self.all_tickets

    def create_ticket_post(self, ticked_id, ticket_post_text):
        TicketPost(ticked_id=ticked_id,
                   ticket_post_author=self.user_name,
                   ticket_post_text=ticket_post_text,
                   ticket_post_order=0,
                   ).save()

    def create_ticket(self, request):
        post_request = request.POST
        ticket = Ticket(author=self.user_name,
                        status='pending', )
        ticket.save()
        self.create_ticket_post(ticket.id, post_request['ticket_post_text'])

        return HttpResponseRedirect('/main/tickets')

    def choose_ticket(self, ticket_id=None):
        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
            if self.check_user_access_to_ticket(ticket):
                return ticket
            else:
                return False
        else:
            ticket = self.all_tickets[0]
            return ticket

    def check_user_access_to_ticket(self, ticket):
        if ticket.author == self.user_name or self.user_name == 'airlove':
            return True
        else:
            return False


def results(request):
    if request.method == "POST":
        NewRequestHandler(request)
        return HttpResponseRedirect('/main/results')
    else:
        user_data = SiteUser(request.user.username)
        all_requests_list = get_list_or_404(Request.objects.order_by('site_seo_concurency'))
        try:
            context = {'all_requests_list': all_requests_list,
                       'orders': user_data.orders,
                       'keywords_ordered': user_data.ordered_keywords,
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
        user_data = SiteUser(request.user.username)
        orders_data = Orders(user_data.id)
        form = NewRequest()

        context = {'all_orders_list': orders_data.unique_order_rows,
                   'orders': user_data.orders,
                   'keywords_ordered': user_data.ordered_keywords,
                   'balance': user_data.balance,
                   'form': form}

        return render(request, 'main/orders.html', context)


def requests_from_order(request, order_id):
    user_data = SiteUser(request.user.username)
    order_data = Order.objects.filter(order_id=order_id)

    if order_data[0].user_id == user_data.id:
        requests_ids = [od.request_id for od in order_data]
        all_requests_list = Request.objects.filter(id__in=requests_ids)

        context = {'all_requests_list': all_requests_list,
                   'orders': user_data.orders,
                   'keywords_ordered': user_data.ordered_keywords,
                   'balance': user_data.balance}

        if request.user.is_staff:
            return render(request, 'main/restricted_requests.html', context)
        else:
            return render(request, 'main/non_restricted_requests.html', context)
    else:
        return HttpResponse('У вас нет доступа к этому заказу')


def balance(request):
    pass


def registration(request):
    if request.method == "POST":
        user = NewUserHandler(request)
        if user.valid:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            login(request, user)
            return HttpResponseRedirect('/main/orders')
        else:
            return render(request, 'main/user_auth/registration.html', {'error':'пароли не совпадают'})
    else:
        form = NewUser()
        context = {
            'form': form,
        }
        return render(request, 'main/user_auth/registration.html', context)


def authorization(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        login(request, user)
        return HttpResponseRedirect('/main/results')
    else:
        form = AuthUser()
        context = {
            'form': form,
        }

        return render(request, 'main/user_auth/authorization.html', context)


def add_new_ticket(request):
    username = request.user.username
    user_data = SiteUser(username)
    tickets_data = Tickets(user_data)
    all_tickets = tickets_data.get_all_user_tickets()

    if request.method == "POST":
        tickets_data.create_ticket(request)
        return HttpResponseRedirect('/main/tickets')

    context = {
        'all_tickets': all_tickets,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance,
    }

    return render(request, 'main/ticket/add_new_ticket.html', context)


def get_ticket_posts_from_ticket(request, ticket_id=None):
    username = request.user.username
    user_data = SiteUser(username)
    tickets_data = Tickets(user_data)

    if request.user.is_staff:
        all_tickets = tickets_data.get_all_admin_tickets()
    else:
        all_tickets = tickets_data.get_all_user_tickets()

    if all_tickets:
        choosen_ticket = tickets_data.choose_ticket(ticket_id)
        if choosen_ticket or request.user.is_staff:
            if request.method == "POST":
                post_request = request.POST
                tickets_data.create_ticket_post(ticket_id, post_request['ticket_post_text'])
                return HttpResponseRedirect(request.path)

            latest_ticket_posts = TicketPost.objects.filter(ticked_id=choosen_ticket.id).order_by('-id')

            context = {
                'all_tickets': all_tickets,
                'latest_ticket': choosen_ticket,
                'latest_ticket_posts': latest_ticket_posts,
                'orders': user_data.orders,
                'user_role': user_data.user_role,
                'keywords_ordered': user_data.ordered_keywords,
                'balance': user_data.balance,
            }

            return render(request, 'main/ticket/ticket.html', context)
        else:
            return HttpResponse('У вас нет доступа к этому тикету')
    else:
        return add_new_ticket(request)


def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/main/authorization')


def close_ticket(request, ticket_id):
    if request.user.is_staff:
        ticket = Ticket.objects.filter(id=ticket_id).update(status='closed', closed=timezone.now())
        return HttpResponseRedirect('/main/tickets')
    else:
        return HttpResponse('У вас нет права закрывать тикеты')