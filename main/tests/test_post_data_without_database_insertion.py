from django.contrib.auth import get_user_model, authenticate, login
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from main.models import UserData, Region

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

    def test_registration_invalid_email(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  }, follow=True)

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_registration_invalid_username(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': '',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_registration_invalid_password(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'test_user',
                                  'password': '123',
                                  'password_again': '123',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_registration_passwords_are_not_same(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_registration_user_exists(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@ya.ru',
                                  'username': 'user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_registration_email_exists(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'tata@nano.com',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '7654321',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertFalse(new_user)

    def test_authorization_success(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'user',
                                  'password': 'password1234',
                                  }, 
                            follow=True)

        username = response.wsgi_request.user.username

        self.assertTrue(username)

    def test_authorization_wrong_password(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'user',
                                  'password': 'password12345',
                                  })

        username = response.wsgi_request.user.username

        self.assertFalse(username)
        
    def test_authorization_wrong_login(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'userk',
                                             'password': 'password123456',
                                            })

        username = response.wsgi_request.user.username

        self.assertFalse(username)

    def test_authorization_wrong_login_and_password(self):
        url = reverse('authorization')

        response = self.anonymous.post(url, {'username': 'userk',
                                  'password': 'password12345',
                                  })

        username = response.wsgi_request.user.username

        self.assertFalse(username)

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

        user = authenticate(request, username='user', password='changed_password')
        login(request, user)
        self.assertTrue(user)

    def test_change_password_passwords_are_not_same(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': 'changed_password',
                                        'second_password': 'changeded_password',
                                        }, follow=True)

        request = response.wsgi_request
        self.user.logout()

        user = authenticate(request, username='user', password='changed_password')
        login(request, user)
        self.assertFalse(user)

    def test_change_password_short_case(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': '',
                                        'second_password': '',
                                        }, follow=True)
        request = response.wsgi_request
        self.user.logout()

        user = authenticate(request, username='user', password='changed_password')
        login(request, user)
        self.assertFalse(user)

    def test_change_password_long_case(self):
        url = reverse('change_password')
        response = self.user.post(url, {'first_password': '1234567890123456789012345678901234567890',
                                        'second_password': '1234567890123456789012345678901234567890',
                                        }, follow=True)
        request = response.wsgi_request
        self.user.logout()

        user = authenticate(request, username='user', password='changed_password')
        login(request, user)
        self.assertFalse(user)

