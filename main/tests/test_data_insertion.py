from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from main.models import Ticket, TicketPost, UserData, Region, Request, RequestQueue, Order


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

    def test_user_add_new_request(self):
        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': 'Lasik',
                             'previous_page': '/orders',
                             'geo': '255'}, follow=True)

        request = Request.objects.get(text='lasik')
        request_id = request.id
        requestqueue = RequestQueue.objects.get(request_id=request_id)

        self.assertTrue(request)
        self.assertTrue(requestqueue)

        request = Request.objects.filter(text='Lasik')
        self.assertFalse(request)


    def test_user_add_new_request_with_no_balance(self):
        user = User.objects.get(username='user')
        user_id = user.id
        user_data = UserData.objects.get(user_id=user_id)
        user_data.balance = 0
        user_data.save()

        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': 'Lasik',
                                        'previous_page': '/orders',
                                        'geo': '255'}, follow=True)

        request = Request.objects.filter(text='lasik')
        self.assertFalse(request)

    def test_user_add_new_multiple_requests(self):
        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': 'Lasik\r\nФРК',
                             'previous_page': '/orders',
                             'geo': '255'}, follow=True)

        request = Request.objects.get(text='lasik')
        request_id = request.id
        requestqueue = RequestQueue.objects.get(request_id=request_id)
        self.assertTrue(request)
        self.assertTrue(requestqueue)

        request = Request.objects.get(text='фрк')
        request_id = request.id
        requestqueue = RequestQueue.objects.get(request_id=request_id)
        self.assertTrue(request)
        self.assertTrue(requestqueue)

    def test_user_adds_empty_request(self):
        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': '',
                             'previous_page': '/orders',
                             'geo': '255'}, follow=True)

        request = Request.objects.all()
        requestqueue = RequestQueue.objects.all()
        user_id = User.objects.get(username='user').id
        balance = UserData.objects.get(user_id=user_id).balance

        self.assertFalse(request)
        self.assertFalse(requestqueue)
        self.assertEqual(100, balance)

    def test_user_adds_empty_request_in_middle(self):
        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': 'Lasik\r\nФРК',
                             'previous_page': '/orders',
                             'geo': '255'}, follow=True)

        requests_amount = len(Request.objects.all())
        requestqueue_amount = len(RequestQueue.objects.all())
        user_id = User.objects.get(username='user').id
        balance = UserData.objects.get(user_id=user_id).balance

        self.assertEqual(2, requests_amount)
        self.assertEqual(2, requestqueue_amount)
        self.assertEqual(99, balance)

    def test_user_adds_requests_to_existing_order(self):
        user = User.objects.get(username='user')
        order = Order.objects.create(user_id=user.id, ordered_keywords_amount=1)

        url = reverse('handle_new_request')
        self.user.post(url, {'requests_list': 'Lasik\r\nФРК',
                             'previous_page': '/orders',
                             'order_id': order.user_order_id,
                             'geo': '255'}, follow=True)

        ordered_requests_count = Order.objects.get(id=order.id).ordered_keywords_amount
        self.assertEqual(3, ordered_requests_count)

    def test_user_add_ticket(self):
        tickets = Ticket.objects.all()
        self.assertFalse(tickets)

        url = reverse('tickets_page')

        self.user.post(url, {'ticket_post_text': 'Текст тикета',
                             'new_ticket': True}, follow=True)

        tickets = Ticket.objects.all()
        self.assertTrue(tickets)
        ticket_post = TicketPost.objects.get(text='Текст тикета').text
        self.assertEqual('Текст тикета', ticket_post)

    def test_user_add_multiple_tickets(self):
        tickets = Ticket.objects.all()
        self.assertFalse(tickets)

        url = reverse('tickets_page')

        self.user.post(url, {'ticket_post_text': 'Первый тикет',
                             'new_ticket': True}, follow=True)

        tickets = Ticket.objects.all()
        self.assertTrue(tickets)
        ticket_post = TicketPost.objects.get(text='Первый тикет').text
        self.assertEqual('Первый тикет', ticket_post)

        url = reverse('tickets_page')

        self.user.post(url, {'ticket_post_text': 'Второй тикет',
                             'new_ticket': True}, follow=True)

        tickets = Ticket.objects.all()
        self.assertTrue(tickets)
        ticket_post = TicketPost.objects.get(text='Второй тикет').text
        self.assertEqual('Второй тикет', ticket_post)

    def test_user_add_ticket_post(self):

        user = User.objects.get(username='user')
        ticket = Ticket.objects.create(author_id=user.id)
        first_ticket_post = TicketPost.objects.create(author_id=user.id, ticket_id=ticket.id, text='Текст первого поста тикета')

        url = reverse('tickets_from', args=(ticket.user_ticket_id,))

        self.user.post(url, {'ticket_post_text': 'Текст второго поста тикета'}, follow=True)

        ticket_posts_amount = len(TicketPost.objects.all())
        second_ticket_post = TicketPost.objects.get(text='Текст второго поста тикета')
        self.assertEqual(2, ticket_posts_amount)
        self.assertEqual('Текст первого поста тикета', first_ticket_post.text)
        self.assertEqual('Текст второго поста тикета', second_ticket_post.text)

    def test_registration_success(self):
        url = reverse('registration')

        self.anonymous.post(url, {'email': 'JdosIuemdklQeudjLkd@yandex.ru',
                                  'username': 'test_user',
                                  'password': '1234567',
                                  'password_again': '1234567',
                                  })

        new_user = User.objects.filter(username='test_user')
        self.assertTrue(new_user)


