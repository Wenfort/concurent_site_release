from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.models import User

from main.models import UserData, Region
from main.tools.password_generator import generate_password
from main.tools.email_sender import MailEngine

from django.contrib import messages

class SiteUser:
    def __init__(self, user):
        self.account_data = user
        self.id = self.account_data.id
        self.user_billing = object
        self.balance = int
        self.orders = int
        self.ordered_keywords = int
        self.region_id = int
        self.region_name = str

        self.__get_user_data()

    def __get_user_data(self):
        self.user_billing = UserData.objects.filter(user_id=self.id).select_related()
        self.user_billing = self.user_billing[0]

        self._get_balance()
        self._get_orders()
        self._get_ordered_requests()
        self._get_region_name()

    def _get_balance(self):
        self.balance = self.user_billing.balance

    def _get_orders(self):
        self.orders = self.user_billing.orders_amount

    def _get_ordered_requests(self):
        self.ordered_keywords = self.user_billing.ordered_keywords

    def _get_region_name(self):
        self.region_id = self.user_billing.region_id
        self.region_name = Region.objects.get(id=self.region_id).name


class NewUserHandler:
    def __init__(self, request):
        self.request = request.POST
        self.user_name = str()
        self.password = str()
        self.password_again = str()
        self.email = str()
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

        if '@' not in self.email and '.' not in self.email:
            self.valid = False
            self.status_messages.append('Пожалуйста, укажите корректный e-mail')

    def check_username_and_password(self):
        all_users = User.objects.all()

        login_is_busy = all_users.filter(username=self.user_name)
        email_is_busy = all_users.filter(email=self.email)

        is_login_length_enough = 6 <= len(self.user_name) <= 30

        if not is_login_length_enough:
            self.valid = False
            self.status_messages.append('Имя пользователя должно быть от 6 до 30 символов')

        is_password_length_enough = 6 <= len(self.password) <= 30

        if not is_password_length_enough:
            self.valid = False
            self.status_messages.append('Длина пароля должна быть от 6 до 30 символов')

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

@login_required
def change_password(request):

    if request.method == "POST":
        post_request = request.POST


        if post_request['first_password'] == post_request['second_password']:
            is_password_length_enough = 6 <= len(post_request['first_password']) <= 30

            if not is_password_length_enough:
                message = 'Длина пароля должна быть от 6 до 30 символов'
                context = {
                    'message': message
                }
                return render(request, 'main/user_auth/change_password.html', context)
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


@login_required
def password_reset(request):
    if request.method == "POST":
        mail_engine = MailEngine(request.POST)

        try:
            user = User.objects.get(email=mail_engine.recipients[0])
            password = generate_password()
            user.set_password(password)
            user.save()

            mail_engine.send_reset_password_mail_via_django(password)
            message = 'Новый пароль отправлен на указанный e-mail. Пожалуйста, проверьте папку "Спам"'
        except:
            message = 'Пользователь с таким e-mail не найден'

        context = {
            'message': message
        }

        return render(request, 'main/user_auth/password_reset.html', context)
    else:
        return render(request, 'main/user_auth/password_reset.html')


@login_required
def balance(request):
    user_data = SiteUser(request.user)
    context = {'orders': user_data.orders,
               'keywords_ordered': user_data.ordered_keywords,
               'balance': user_data.balance
               }
    return render(request, 'main/balance.html', context)


def registration(request):
    if request.user.is_authenticated:
        return HttpResponse('Вы уже зарегистрированы')

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
        return render(request, 'main/user_auth/registration.html')


def authorization(request):
    if request.user.is_authenticated:
        return HttpResponse('Вы уже авторизировались')

    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return HttpResponseRedirect('/results')
        else:
            context = {
                'error': 'Логин и пароль не совпадают'
            }

            return render(request, 'main/user_auth/authorization.html', context)
    else:
        return render(request, 'main/user_auth/authorization.html')


def change_region(request):
    user_id = request.user.id
    new_region = request.POST['region']
    previous_url = request.POST['previous_url']
    if new_region:
        try:
            new_region_id = Region.objects.get(name=new_region).id
            user = UserData.objects.filter(user_id=user_id)
            user.update(region_id=new_region_id)
            messages.success(request, 'Регион успешно изменен')
        except:
            messages.error(request, f'К сожалению, регион {new_region} не поддерживается')
    else:
        messages.error(request, 'Поле "регион" не может быть пустым')

    return HttpResponseRedirect(previous_url)


@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/authorization')
