from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from main.models import UserData, Region, Request, Ticket, TicketPost, Order
from bs4 import BeautifulSoup


class LogicTestCase(TestCase):

    def setUp(self):
        self.anonymous = Client()
        self.user = Client()

        user_data = get_user_model().objects.create_user(
            username='user',
            email='tata@nano.com',
            password='password1234',
        )

        Region.objects.create(id=255, name='Россия')
        Region.objects.create(id=11181, name='Лангепас')

        UserData.objects.create(user_id=user_data.id, balance=100, orders_amount=0, ordered_keywords=0, region_id=255)

        self.user.force_login(user_data)

    def test_anonymous_order_confirmation(self):
        url = reverse('user_confirmation')

        response = self.anonymous.post(url, {'requests_list': 'Lasik\r\nФРК',
                                             'previous_page': '/orders',
                                             'geo': '255'})

        all_requests = Request.objects.all()

        self.assertFalse(all_requests)
        self.assertEqual(302, response.status_code)

    def test_user_order_confirmation(self):
        url = reverse('user_confirmation')

        response = self.user.post(url, {'requests_list': 'Lasik\r\nФРК',
                                        'previous_page': '/orders',
                                        'geo': '255'})
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Lasik')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('ФРК')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Выбранный регион: Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Запросов в заказе: 2')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Будет списано: 1.0 руб.')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertEqual(-1, text_response_position_in_text)


    def test_user_order_confirmation_zero_requests_first_case(self):
        url = reverse('user_confirmation')

        response = self.user.post(url, {'requests_list': '\r\n',
                                        'previous_page': '/orders',
                                        'geo': '255'})
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Выбранный регион: Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Запросов в заказе: 0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Будет списано: 0.0 руб.')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertEqual(-1, text_response_position_in_text)
        text_response_position_in_text = text.find('Lasik')
        self.assertEqual(-1, text_response_position_in_text)

    def test_user_order_confirmation_zero_requests_second_case(self):
        url = reverse('user_confirmation')

        response = self.user.post(url, {'requests_list': '',
                                        'previous_page': '/orders',
                                        'geo': '255'})
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Выбранный регион: Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Запросов в заказе: 0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Будет списано: 0.0 руб.')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertEqual(-1, text_response_position_in_text)
        text_response_position_in_text = text.find('Lasik')
        self.assertEqual(-1, text_response_position_in_text)

    def test_user_order_page(self):
        user = User.objects.get(username='user')
        Order.objects.create(user_id=user.id, ordered_keywords_amount=1, user_order_id=1)
        Order.objects.create(user_id=user.id, ordered_keywords_amount=2, user_order_id=2)

        url = reverse('get_orders_page')

        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('#1')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('#2')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertGreater(text_response_position_in_text, 0)

        text_response_position_in_text = text.find('Lasik')
        self.assertEqual(-1, text_response_position_in_text)

    def test_user_requests_from_order(self):
        user = User.objects.get(username='user')
        first_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=1, user_order_id=1)
        second_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=2, user_order_id=2)

        Request.objects.create(text='lasik', region_id=255, order_id=first_order.id)
        Request.objects.create(text='ФРК', region_id=255, order_id=first_order.id)
        Request.objects.create(text='Коррекция зрения', region_id=255, order_id=second_order.id)

        url = reverse('requests_from_order', args=(first_order.user_order_id,))

        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('lasik')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('ФРК')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertGreater(text_response_position_in_text, 0)

        url = reverse('requests_from_order', args=(second_order.user_order_id,))

        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Коррекция зрения')
        self.assertGreater(text_response_position_in_text, 0)

    def test_get_all_ordered_requests(self):
        user = User.objects.get(username='user')
        first_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=1, user_order_id=1)
        second_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=2, user_order_id=2)

        Request.objects.create(text='lasik', region_id=255, order_id=first_order.id)
        Request.objects.create(text='ФРК', region_id=255, order_id=first_order.id)
        Request.objects.create(text='ласик', region_id=255, order_id=first_order.id)
        Request.objects.create(text='Коррекция зрения', region_id=255, order_id=second_order.id)
        Request.objects.create(text='Операция на глаза', region_id=255, order_id=second_order.id)

        url = reverse('results')
        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('lasik')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('ФРК')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Операция на глаза')
        self.assertGreater(text_response_position_in_text, 0)

    def test_user_change_region_success(self):
        url = reverse('change_region')
        response = self.user.post(url, {'region': 'Лангепас',
                                        'previous_url': '/orders'},
                                  follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Лангепас')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

    def test_user_change_empty_region(self):
        url = reverse('change_region')
        response = self.user.post(url, {'region': '',
                                        'previous_url': '/orders'},
                                  follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Россия')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Поле "регион" не может быть пустым')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

    def test_user_change_non_existing_region(self):
        url = reverse('change_region')
        response = self.user.post(url, {'region': 'Нижняя бургундия',
                                        'previous_url': '/orders'},
                                  follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('К сожалению, регион Нижняя бургундия не поддерживается')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

    def test_user_add_ticket_page(self):
        user = User.objects.get(username='user')
        ticket = Ticket.objects.create(author_id=user.id)
        TicketPost.objects.create(text='Первый пост тикета', author_id=user.id, ticket_id=ticket.id)

        url = reverse('tickets_page')
        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Тикет #1')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Пожалуйста, подробно опишите что идет не так :)')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

    def test_user_views_ticket_page(self):
        user = User.objects.get(username='user')
        ticket = Ticket.objects.create(author_id=user.id)
        TicketPost.objects.create(text='Первый пост тикета', author_id=user.id, ticket_id=ticket.id)

        url = reverse('tickets_from', args=(ticket.user_ticket_id,))
        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Тикет #1')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Первый пост тикета')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Баланс:\n100.0 рублей')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего заказов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Всего запросов:\n0')
        self.assertGreater(text_response_position_in_text, 0)
        text_response_position_in_text = text.find('Сменить пароль\nПоддержка\nВыйти')
        self.assertGreater(text_response_position_in_text, 0)

    def test_registration_success(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@yandex.ru',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '1234567'
                                  }, follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text

        text_response_position_in_text = text.find('Введите каждый запрос с новой строки')
        self.assertGreater(text_response_position_in_text, 0)

    def test_registration_invalid_email(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  }, follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        no_at_in_email_position_in_text = text.find('Пожалуйста, укажите корректный e-mail')
        self.assertGreater(no_at_in_email_position_in_text, 0)

    def test_registration_invalid_username(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': '',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        invalid_login_position_in_text = text.find('Имя пользователя должно быть от 6 до 30 символов')
        self.assertGreater(invalid_login_position_in_text, 0)

    def test_registration_invalid_password(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'test_user',
                                  'password': '123',
                                  'password_again': '123',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        invalid_login_position_in_text = text.find('Длина пароля должна быть от 6 до 30 символов')
        self.assertGreater(invalid_login_position_in_text, 0)

    def test_registration_passwords_are_not_same(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        passwords_are_not_same_position_in_text = text.find('Пароли не совпадают')
        self.assertGreater(passwords_are_not_same_position_in_text, 0)

    def test_registration_user_exists(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        user_exists_position_in_text = text.find('Логин уже занят')
        self.assertGreater(user_exists_position_in_text, 0)

    def test_registration_email_exists(self):
        url = reverse('registration')

        response = self.anonymous.post(url, {'email': 'tata@nano.com',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        user_exists_position_in_text = text.find('Email уже занят')
        self.assertGreater(user_exists_position_in_text, 0)

    def test_authorization_wrong_password(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'user',
                                  'password': 'password12345',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Логин и пароль не совпадают')
        self.assertGreater(text_response_position_in_text, 0)

    def test_authorization_wrong_login(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'userk',
                                  'password': 'password123456',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Логин и пароль не совпадают')
        self.assertGreater(text_response_position_in_text, 0)

    def test_authorization_wrong_login_and_password(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'userk',
                                  'password': 'password12345',
                                  })

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Логин и пароль не совпадают')
        self.assertGreater(text_response_position_in_text, 0)

    def test_change_password_success(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': 'changed_password',
                                        'second_password': 'changed_password',
                                        })
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Пароль успешно изменен')
        self.assertGreater(text_response_position_in_text, 0)

    def test_change_password_passwords_are_not_same(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': 'changed_password',
                                        'second_password': 'changeded_password',
                                        }, follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Пароли не совпадают')
        self.assertGreater(text_response_position_in_text, 0)

    def test_change_password_short_case(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': '',
                                        'second_password': '',
                                        }, follow=True)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Длина пароля должна быть от 6 до 30 символов')
        self.assertGreater(text_response_position_in_text, 0)

    def test_change_password_long_case(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': '1234567890123456789012345678901234567890',
                                        'second_password': '1234567890123456789012345678901234567890',
                                        }, follow=True)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        text_response_position_in_text = text.find('Длина пароля должна быть от 6 до 30 символов')
        self.assertGreater(text_response_position_in_text, 0)

    def test_sorting_on_order_page_descending(self):
        user = User.objects.get(username='user')
        first_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=1, user_order_id=1)
        second_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=2, user_order_id=2)

        Request.objects.create(text='lasik', region_id=255, order_id=first_order.id, average_age=40)
        Request.objects.create(text='ФРК', region_id=255, order_id=first_order.id, average_age=35)
        Request.objects.create(text='ласик', region_id=255, order_id=first_order.id, average_age=48)
        Request.objects.create(text='Коррекция зрения', region_id=255, order_id=second_order.id, average_age=55)
        Request.objects.create(text='Операция на глаза', region_id=255, order_id=second_order.id, average_age=90)

        url = reverse('results')
        response = self.user.get(url, {'sort': '-avg_old'})
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        all_requests = soup.find_all('td')
        first_request_text = all_requests[0].text
        last_request_text = all_requests[-3].text
        self.assertEqual('Операция на глаза', first_request_text)
        self.assertEqual('ФРК', last_request_text)

    def test_sorting_on_order_page_ascending(self):
        user = User.objects.get(username='user')
        first_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=1, user_order_id=1)
        second_order = Order.objects.create(user_id=user.id, ordered_keywords_amount=2, user_order_id=2)

        Request.objects.create(text='lasik', region_id=255, order_id=first_order.id, average_age=40)
        Request.objects.create(text='ФРК', region_id=255, order_id=first_order.id, average_age=35)
        Request.objects.create(text='ласик', region_id=255, order_id=first_order.id, average_age=48)
        Request.objects.create(text='Коррекция зрения', region_id=255, order_id=second_order.id, average_age=55)
        Request.objects.create(text='Операция на глаза', region_id=255, order_id=second_order.id, average_age=90)

        url = reverse('results')
        response = self.user.get(url, {'sort': 'avg_old'})
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        all_requests = soup.find_all('td')
        first_request_text = all_requests[0].text
        last_request_text = all_requests[-3].text
        self.assertEqual('ФРК', first_request_text)
        self.assertEqual('Операция на глаза', last_request_text)