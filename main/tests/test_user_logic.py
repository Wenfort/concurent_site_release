from django.contrib.auth import get_user_model, authenticate, login
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

import main
from main.models import UserData, Region
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

    def test_change_region_success(self):
        url = reverse('change_region')
        previous_url = reverse('get_orders_page')
        self.user.post(url, {'region': 'Лангепас',
                                        'previous_url': previous_url})

        url = reverse('get_orders_page')
        response = self.user.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        langepas_text_position = text.find('Лангепас')
        self.assertGreater(langepas_text_position, 0)

    def test_change_region_if_region_does_not_exists(self):
        url = reverse('change_region')
        previous_url = reverse('get_orders_page')

        with self.assertRaisesMessage(main.models.Region.DoesNotExist, 'Region matching query does not exist.'):
            self.user.post(url, {'region': 'Южная Бургундия',
                                 'previous_url': previous_url})

    def test_change_region_if_empty_input(self):
        url = reverse('change_region')
        previous_url = reverse('get_orders_page')

        response = self.user.post(url, {'region': '',
                                        'previous_url': previous_url},
                                  follow=True)

        content = response.content

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.text
        empty_field_text_position = text.find('Поле "регион" не может быть пустым')
        self.assertGreater(empty_field_text_position, 0)

    def test_registration_success(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@yandex.ru',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  })

        test_user = User.objects.get(username='test_user')
        self.assertEqual('test_user', test_user.username)
        self.assertEqual('jdosiuemdklqeudjlkd@yandex.ru', test_user.email)

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

    def test_authorization_success(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'user',
                                  'password': 'password1234',
                                  }, 
                            follow=True)

        username = response.wsgi_request.user.username

        self.assertEqual('user', username)

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

    def test_change_password_anonymous_send(self):
        url = reverse('change_password')

        response = self.anonymous.post(url, {'first_password': '123456',
                                             'second_password': '123456',
                                              })

        self.assertEqual('/authorization/?next=/change_password', response.url)

    def test_change_password_success(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': 'changed_password',
                                             'second_password': 'changed_password',
                                             })
        request = response.wsgi_request
        self.user.logout()

        user = authenticate(request, username='user', password='change_password')
        self.assertFalse(user)
        user = authenticate(request, username='user', password='changed_password')
        login(request, user)
        self.assertEqual(True, user.is_authenticated)