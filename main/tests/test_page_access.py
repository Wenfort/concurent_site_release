from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from main.models import UserData, Region
from bs4 import BeautifulSoup


class LogicTestCase(TestCase):

    @classmethod
    def setUpClass(self):
        self.not_logged_client = Client()
        self.logged_client = Client()
        self.admin_client = Client()

        admin_account_data = get_user_model().objects.create_superuser(
            username='admin', email='test@ya.ru', password='123')

        user_data = get_user_model().objects.create_user(
            username='user',
            email='tata@nano.com',
            password='password1234',
        )

        Region.objects.create(id=255, name='Россия')

        UserData.objects.create(user_id=1, balance=100, orders_amount=0, ordered_keywords=0, region_id=255)
        UserData.objects.create(user_id=2, balance=100, orders_amount=0, ordered_keywords=0, region_id=255)

        self.admin_client.force_login(admin_account_data)
        self.logged_client.force_login(user_data)

    @classmethod
    def tearDownClass(self):
        pass

    def test_index_not_logged_in(self):
        url = reverse('index')

        response = self.not_logged_client.get(url)
        request = response.wsgi_request
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization', response.url)
        self.assertEqual('', request.user.username)
        self.assertEqual(True, request.user.is_anonymous)

    def test_index_logged_client(self):
        url = reverse('index')

        response = self.logged_client.get(url)
        request = response.wsgi_request
        self.assertEqual(302, response.status_code)
        self.assertEqual('/orders', response.url)
        self.assertEqual('user', request.user.username)
        self.assertEqual(False, request.user.is_anonymous)

    def test_orders_page_not_logged_in(self):
        url = reverse('get_orders_page')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/orders', response.url)

    def test_orders_page_logged_client(self):
        url = reverse('get_orders_page')

        response = self.logged_client.get(url)
        request = response.wsgi_request
        self.assertEqual(200, response.status_code)
        self.assertEqual('/orders', request.path)

    def test_not_existing_order_page_not_logged_in(self):
        url = reverse('requests_from_order', args=(1,))

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/orders/1', response.url)

    def test_not_existing_order_page_logged_client(self):
        url = reverse('requests_from_order', args=(1,))

        response = self.logged_client.get(url)
        self.assertEqual(404, response.status_code)

    def test_not_existing_order_page_logged_admin(self):
        url = reverse('requests_from_order', args=(1,))

        response = self.admin_client.get(url)
        self.assertEqual(404, response.status_code)

    def test_results_page_not_logged_in(self):
        url = reverse('results')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/results', response.url)

    def test_results_page_logged_client(self):
        url = reverse('results')

        response = self.logged_client.get(url)
        request = response.wsgi_request
        self.assertEqual(200, response.status_code)
        self.assertEqual('/results', request.path)

    def test_results_page_admin_client(self):
        url = reverse('results')

        response = self.admin_client.get(url)
        request = response.wsgi_request
        self.assertEqual(200, response.status_code)
        self.assertEqual('/results', request.path)

    def test_change_password_page_not_logged_client(self):
        url = reverse('change_password')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/change_password', response.url)

    def test_change_password_page_logged_client(self):
        url = reverse('change_password')

        response = self.logged_client.get(url)
        request = response.wsgi_request
        self.assertEqual(200, response.status_code)
        self.assertEqual('/change_password', request.path)

    def test_change_password_page_admin_client(self):
        url = reverse('change_password')

        response = self.admin_client.get(url)
        request = response.wsgi_request
        self.assertEqual(200, response.status_code)
        self.assertEqual('/change_password', request.path)

    def test_registration_page_not_logged_client(self):
        url = reverse('registration')

        response = self.not_logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        email_position_in_text = text.find('Электронная почта')
        login_position_in_text = text.find('Имя пользователя')
        password_position_in_text = text.find('Пароль')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/registration', request.path)
        self.assertGreater(email_position_in_text, 0)
        self.assertGreater(login_position_in_text, 0)
        self.assertGreater(password_position_in_text, 0)

    def test_registration_page_logged_client(self):
        url = reverse('registration')

        response = self.logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request

        self.assertEqual(200, response.status_code)
        self.assertEqual('/registration', request.path)
        self.assertEqual('Вы уже зарегистрированы', text)

    def test_registration_page_admin_client(self):
        url = reverse('registration')

        response = self.admin_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request

        self.assertEqual(200, response.status_code)
        self.assertEqual('/registration', request.path)
        self.assertEqual('Вы уже зарегистрированы', text)

    def test_authorization_page_not_logged_client(self):
        url = reverse('authorization')

        response = self.not_logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        login_position_in_text = text.find('Имя пользователя')
        password_position_in_text = text.find('Пароль')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/authorization/', request.path)
        self.assertGreater(login_position_in_text, 0)
        self.assertGreater(password_position_in_text, 0)

    def test_authorization_page_logged_client(self):
        url = reverse('authorization')

        response = self.logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request

        self.assertEqual(200, response.status_code)
        self.assertEqual('/authorization/', request.path)
        self.assertEqual('Вы уже авторизировались', text)

    def test_authorization_page_admin_client(self):
        url = reverse('authorization')

        response = self.admin_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request

        self.assertEqual(200, response.status_code)
        self.assertEqual('/authorization/', request.path)
        self.assertEqual('Вы уже авторизировались', text)

    def test_password_reset_page_not_logged_client(self):
        url = reverse('password_reset')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/password_reset', response.url)

    def test_password_reset_page_logged_client(self):
        url = reverse('password_reset')

        response = self.logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        email_position_in_text = text.find('Укажите ваш e-mail')
        reset_confirmation_position_in_text = text.find('Сбросить пароль')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/password_reset', request.path)
        self.assertGreater(email_position_in_text, 0)
        self.assertGreater(reset_confirmation_position_in_text, 0)

    def test_password_reset_page_admin_client(self):
        url = reverse('password_reset')

        response = self.admin_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        email_position_in_text = text.find('Укажите ваш e-mail')
        reset_confirmation_position_in_text = text.find('Сбросить пароль')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/password_reset', request.path)
        self.assertGreater(email_position_in_text, 0)
        self.assertGreater(reset_confirmation_position_in_text, 0)

    def test_tickets_page_not_logged_client(self):
        url = reverse('tickets_page')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/tickets', response.url)

    def test_tickets_page_logged_client(self):
        url = reverse('tickets_page')

        response = self.logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        add_new_ticket_position_in_text = text.find('Создать новый тикет')
        ticket_form_description_position_in_text = text.find('Пожалуйста, подробно опишите что идет не так :)')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/tickets', request.path)
        self.assertGreater(add_new_ticket_position_in_text, 0)
        self.assertGreater(ticket_form_description_position_in_text, 0)

    def test_tickets_page_admin_client(self):
        url = reverse('tickets_page')

        response = self.admin_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        add_new_ticket_position_in_text = text.find('Создать новый тикет')
        ticket_form_description_position_in_text = text.find('Пожалуйста, подробно опишите что идет не так :)')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/tickets', request.path)
        self.assertGreater(add_new_ticket_position_in_text, 0)
        self.assertGreater(ticket_form_description_position_in_text, 0)

    def test_specific_ticket_page_not_logged_client(self):
        url = reverse('tickets_from', args=(1,))

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/tickets/1', response.url)

    def test_specific_ticket_page_logged_client(self):
        url = reverse('tickets_from', args=(1,))

        response = self.logged_client.get(url)
        self.assertEqual(404, response.status_code)

    def test_specific_ticket_page_admin_client(self):
        url = reverse('tickets_from', args=(1,))

        response = self.admin_client.get(url)
        self.assertEqual(404, response.status_code)

    def test_balance_page_not_logged_client(self):
        url = reverse('balance')

        response = self.not_logged_client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/authorization/?next=/balance', response.url)

    def test_balance_page_logged_client(self):
        url = reverse('balance')

        response = self.logged_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        header_position_in_text = text.find('Пополнение баланса пока не работает.')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/balance', request.path)
        self.assertGreater(header_position_in_text, 0)

    def test_balance_page_admin_client(self):
        url = reverse('balance')

        response = self.admin_client.get(url)
        html = response.content
        text = BeautifulSoup(html, 'html.parser').text
        request = response.wsgi_request
        header_position_in_text = text.find('Пополнение баланса пока не работает.')

        self.assertEqual(200, response.status_code)
        self.assertEqual('/balance', request.path)
        self.assertGreater(header_position_in_text, 0)
