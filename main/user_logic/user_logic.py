from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout as django_logout
from main.models import UserData, Region
from django.contrib.auth.models import User
from main.tools.password_generator import generate_password

from django.contrib import messages

class SiteUser:
    def __init__(self, user):
        self.user = user
        self.id = self.user.id
        self.user_billing = object
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
        self.user_billing = UserData.objects.get(user_id=self.id)

    def get_user_role(self):
        if self.user.is_staff:
            self.user_role = 'admin'
        else:
            self.user_role = 'user'

    def get_balance(self):
        self.balance = self.user_billing.balance

    def get_orders(self):
        self.orders = self.user_billing.orders_amount

    def get_ordered_requests(self):
        self.ordered_keywords = self.user_billing.ordered_keywords

    def get_region(self):
        self.region_id = self.user_billing.region_id
        self.region = Region.objects.get(id=self.region_id).name


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
        UserData(user_id=new_user.id, balance=0).save()

    def compare_passwords(self):
        return self.password == self.password_again


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

        post_request = request.POST
        recipients = post_request['email'].lower(),

        try:
            user = User.objects.get(email=recipients[0])
            password = generate_password()
            user.set_password(password)
            user.save()

            send_mail('Письмо с паролем',
                      f'Ваш временный пароль: {password}. Пожалуйста, смените его сразу после авторизации. Ссылка для авторизации: https://seonior.ru/authorization',
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


def balance(request):
    user_data = SiteUser(request.user.id)
    context = {'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance
               }
    return render(request, 'main/balance.html', context)


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
                context = {
                    'errors_list': user.status_messages,
                    'status': 'retry',
                    'username': request.POST['username'],
                    'email': request.POST['email']
                }
                return render(request, 'main/user_auth/registration.html', context)
        else:
            context = {
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
                try:
                    return HttpResponseRedirect(request.GET['next'])
                except:
                    return HttpResponseRedirect('/results')
            else:
                context = {
                    'error': 'Логин и пароль не совпадают'
                }

                return render(request, 'main/user_auth/authorization.html', context)
        else:
            context = {
            }

            return render(request, 'main/user_auth/authorization.html', context)


def change_region(request):
    user_id = request.user.id
    new_region = request.POST['region']
    previous_url = request.POST['previous_url']
    if new_region:
        new_region_id = Region.objects.get(name=new_region).region_id
        user = UserData.objects.filter(user_id=user_id)
        user.update(region_id=new_region_id)
        messages.success(request, 'Регион успешно изменен')
    else:
        messages.error(request, 'Поле "регион" не может быть пустым')

    return HttpResponseRedirect(previous_url)


def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/authorization')
