from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.shortcuts import render, get_list_or_404, redirect
from django.contrib.auth import authenticate, login, logout as django_logout
from django.utils import timezone
from .models import Request, RequestQueue, UserData, Order, OrderStatus, TicketPost, Ticket
from django.contrib.auth.models import User
from .password_generator import generate_password

from .forms import NewRequest, NewUser, AuthUser, ChangePassword


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class SiteUser:
    def __init__(self, user_id):
        self.id = user_id
        self.user = object
        self.user_role = str
        self.balance = int
        self.orders = int
        self.ordered_keywords = int

        self.get_data()
        self.get_user_role()
        self.get_balance()
        self.get_orders()
        self.get_ordered_requests()


    def get_data(self):
        self.user = UserData.objects.get(user_id=self.id)

    def get_user_role(self):
        if self.id == 17:
            self.user_role = 'admin'
        else:
            self.user_role = 'user'

    def get_balance(self):
        self.balance = self.user.balance

    def get_orders(self):
        self.orders = self.user.orders_amount

    def get_ordered_requests(self):
        self.ordered_keywords = self.user.ordered_keywords


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
        self.unique_order_rows = OrderStatus.objects.filter(user_id=self.user_id)

    def all_ordered_requests(self):
        ordered_requests_ids = [order.request_id for order in self.all_order_rows]
        return Request.objects.filter(request_id__in=ordered_requests_ids)

    def all_requests_from_order(self, order_id):
        ordered_requests_ids = [order.request_id for order in self.all_order_rows.filter(order_id=order_id)]
        return Request.objects.filter(request_id__in=ordered_requests_ids)


class NewRequestHandler:
    def __init__(self, request):
        self.request = request.POST
        self.user_id = request.user.id
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
        self.update_user_order_status()
        self.update_user_orders()

        self.update_user_balance()

    def get_user_data(self):
        self.user_data = SiteUser(self.user_id)

    def make_requests_list(self):
        requests_list = self.request['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.split('\n')
        self.requests_list = requests_list

    def add_new_requests_to_database(self):
        for request in self.requests_list:
            if Request.objects.filter(request_text=request):
                pass
            else:
                RequestQueue(request_text=request).save()
                Request(request_text=request).save()

    def get_order_id(self):
        try:
            self.order_id = Order.objects.latest('pk').id + 1
        except:
            self.order_id = 1

    def get_new_requests_id(self):
        self.new_requests = Request.objects.filter(request_text__in=self.requests_list)

    def calculate_new_requests_amount(self):
        self.new_requests_amount = len(self.new_requests)

    def update_user_orders(self):
        for new_request in self.new_requests:
            Order(request_id=new_request.request_id,
                  user_id=self.user_id,
                  order_id=self.order_id
                  ).save()

    def update_user_order_status(self):
        OrderStatus(order_id=self.order_id,
                    user_id=self.user_id,
                    ordered_keywords_amount=self.new_requests_amount).save()

    def update_user_balance(self):
        user = UserData.objects.filter(user_id=self.user_id)
        user.update(balance=self.user_data.balance - self.new_requests_amount,
                    orders_amount=self.user_data.orders + 1,
                    ordered_keywords=self.user_data.ordered_keywords + self.new_requests_amount,
                    )



class NewUserHandler:
    def __init__(self, request):
        self.request = request.POST
        self.user_name = str
        self.password = str
        self.password_again = str
        self.email = str
        self.valid = True
        self.status_messages = list()

        self.get_user_name()

        self.get_user_password()
        self.get_user_email()
        self.check_username_and_password()

        if not self.compare_passwords():
            self.valid = False
            self.status_messages.append('Пароли не совпадают')

        if self.valid:
            self.create_user()

    def get_user_name(self):
        self.user_name = self.request['username']

    def get_user_password(self):
        self.password = self.request['password']
        self.password_again = self.request['password_again']

    def get_user_email(self):
        self.email = self.request['email'].lower()

    def check_username_and_password(self):
        all_users = User.objects.all()

        login_is_busy = all_users.filter(username=self.user_name)
        email_is_busy = all_users.filter(email=self.email)

        if login_is_busy:
            self.valid = False
            self.status_messages.append('Логин уже занят')

        if email_is_busy:
            self.valid = False
            self.status_messages.append('Email уже занят')



    def create_user(self):
        new_user = User.objects.create_user(self.user_name, self.email, self.password)
        UserData(user_id=new_user.id, balance=50).save()

    def compare_passwords(self):
        return self.password == self.password_again


class Tickets:

    def __init__(self, user_data):
        self.user_id = user_data.id
        self.user_role = user_data.user_role
        self.all_tickets = object


    def get_all_user_tickets(self):
        self.all_tickets = Ticket.objects.filter(author_id=self.user_id).order_by('-ticket_id')
        return self.all_tickets

    def get_all_admin_tickets(self):
        self.all_tickets = Ticket.objects.filter(status='pending').order_by('-ticket_id')
        return self.all_tickets

    def create_ticket_post(self, ticket_id, ticket_post_text):

        TicketPost(ticket_id=ticket_id,
                   ticket_post_author_id=self.user_id,
                   ticket_post_text=ticket_post_text,
                   ticket_post_order=0,
                   ).save()

    def create_ticket(self, request):
        post_request = request.POST

        ticket = Ticket(author_id=self.user_id,
                        status='pending', )
        ticket.save()
        self.create_ticket_post(ticket.ticket_id, post_request['ticket_post_text'])

        return HttpResponseRedirect('/tickets')

    def choose_ticket(self, ticket_id=None):
        if ticket_id:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
            if self.check_user_access_to_ticket(ticket):
                return ticket
            else:
                return False
        else:
            ticket = self.all_tickets[0]
            return ticket

    def check_user_access_to_ticket(self, ticket):
        if ticket.author_id == self.user_id or self.user_role == 'admin':
            return True
        else:
            return False

    def close_ticket(self, ticket_id):
        if self.user_role == 'admin':
            Ticket.objects.filter(ticket_id=ticket_id).update(status='closed', closed=timezone.now())
            return HttpResponseRedirect('/tickets')
        else:
            return HttpResponse('У вас нет права закрывать тикеты')



def results(request):
    if request.method == "POST":
        NewRequestHandler(request)
        return HttpResponseRedirect('/results')
    else:
        user_data = SiteUser(request.user.id)
        if request.user.is_staff:
            all_requests = Request.objects.all().order_by('-site_seo_concurency')

            context = {
                'all_requests': all_requests,
                'orders': user_data.orders,
                'keywords_ordered': user_data.ordered_keywords,
                'balance': user_data.balance,
            }

            return render(request, 'main/restricted_requests.html', context)
        else:
            order_data = Orders(user_data.id)
            all_user_requests = order_data.all_ordered_requests()

            context = {
                'all_requests': all_user_requests,
                'orders': user_data.orders,
                'keywords_ordered': user_data.ordered_keywords,
                'balance': user_data.balance,
            }

        return render(request, 'main/non_restricted_requests.html', context)



def get_orders_page(request):
    if request.method == "POST":
        NewRequestHandler(request)
        return HttpResponseRedirect('/orders')
    else:
        user_data = SiteUser(request.user.id)
        orders_data = Orders(user_data.id)
        form = NewRequest()

        context = {'all_orders_list': orders_data.unique_order_rows,
                   'orders': user_data.orders,
                   'keywords_ordered': user_data.ordered_keywords,
                   'balance': user_data.balance,
                   'form': form}

        return render(request, 'main/orders.html', context)



def requests_from_order(request, order_id):
    user_data = SiteUser(request.user.id)
    order_data = Orders(user_data.id)

    all_requests = order_data.all_requests_from_order(order_id)
    if all_requests:
        context = {'all_requests': all_requests,
                   'orders': user_data.orders,
                   'keywords_ordered': user_data.ordered_keywords,
                   'balance': user_data.balance}

        if request.user.is_staff:
            return render(request, 'main/restricted_requests.html', context)
        else:
            return render(request, 'main/non_restricted_requests.html', context)
    else:
        return HttpResponse('У вас нет доступа к этой странице')


def balance(request):
    pass


def registration(request):
    if request.user.is_authenticated:
        return HttpResponse('Вы уже зарегистрированы')
    else:
        if request.method == "POST":
            user = NewUserHandler(request)
            if user.valid:
                user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                login(request, user)
                return HttpResponseRedirect('/orders')
            else:
                return render(request, 'main/user_auth/registration.html', {'errors_list':user.status_messages})
        else:
            form = NewUser()
            context = {
                'form': form,
            }
            return render(request, 'main/user_auth/registration.html', context)



def authorization(request):
    if request.user.is_authenticated:
        return HttpResponse('Вы уже авторизировались')
    else:
        if request.method == "POST":
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user:
                login(request, user)
                return HttpResponseRedirect('/results')
            else:
                form = AuthUser()
                context = {
                    'form': form,
                    'error': 'Логин и пароль не совпадают'
                }

                return render(request, 'main/user_auth/authorization.html', context)
        else:
            form = AuthUser()
            context = {
                'form': form,
            }

            return render(request, 'main/user_auth/authorization.html', context)


def add_new_ticket(request):
    user_data = SiteUser(request.user.id)
    tickets_data = Tickets(user_data)

    if request.user.is_staff:
        all_tickets = tickets_data.get_all_admin_tickets()
    else:
        all_tickets = tickets_data.get_all_user_tickets()


    if request.method == "POST":
        tickets_data.create_ticket(request)
        return HttpResponseRedirect('/tickets')

    context = {
        'all_tickets': all_tickets,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance,
    }

    return render(request, 'main/ticket/add_new_ticket.html', context)


def get_ticket_posts_from_ticket(request, ticket_id=None):
    user_data = SiteUser(request.user.id)
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

                if ticket_id == None:
                    ticket_id = choosen_ticket.ticket_id

                tickets_data.create_ticket_post(ticket_id, post_request['ticket_post_text'])
                return HttpResponseRedirect(request.path)

            latest_ticket_posts = TicketPost.objects.filter(ticket_id=choosen_ticket.ticket_id).order_by('-ticket_post_id')

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
    return HttpResponseRedirect('/authorization')


def close_ticket(request, ticket_id):
    user_data = SiteUser(request.user.id)
    ticket_data = Tickets(user_data)

    return ticket_data.close_ticket(ticket_id)


def change_password(request):

    if request.method == "POST":
        post_request = request.POST
        if post_request['first_password'] == post_request['second_password']:
            password = post_request['first_password']
            username = request.user.username
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            user = authenticate(request, username=username, password=password)
            login(request, user)

            message = 'Пароль успешно изменен'
        else:
            message = 'Пароли не совпадают'

        context = {
            'message': message
        }
        return render(request, 'main/user_auth/change_password.html', context)

    else:
        return render(request, 'main/user_auth/change_password.html')

def password_reset(request):
    if request.user.is_authenticated:
        return HttpResponse('Вы уже авторизировались')
    if request.method == "POST":
        recipients = list()
        post_request = request.POST
        recipients.append(post_request['email'].lower())

        try:
            user = User.objects.get(email=recipients[0])
            password = generate_password()
            user.set_password(password)
            user.save()

            send_mail('Письмо с паролем',
                      f'Ваш временный пароль: {password}. Пожалуйста, смените его сразу после авторизации.',
                      'admin@seonior.ru', recipients)
            message = 'Новый пароль отправлен на указанный e-mail. Пожалуйста, проверьте папку "Спам"'
        except:
            message = 'Пользователь с таким e-mail не найден'

        context = {
            'message': message
        }

        return render(request, 'main/user_auth/password_reset.html', context)
    else:
        return render(request, 'main/user_auth/password_reset.html')
