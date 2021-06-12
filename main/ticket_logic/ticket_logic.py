from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone
from main.models import TicketPost, Ticket
from main.user_logic.user_logic import SiteUser


class TicketEngine:

    def __init__(self, request, ticket_id=0):
        self.request = request
        self.user_id = request.user.id
        self.is_staff = request.user.is_staff
        self.post_data = request.POST
        self.ticket_id = ticket_id
        self.global_ticket_id = int()
        self.is_ticket_owner = bool()

    def get_tickets_list(self):
        if self.is_staff:
            return Ticket.objects.filter()
        else:
            return Ticket.objects.filter(author_id=self.user_id)

    def get_posts_from_ticket(self):
        all_posts_from_ticket = TicketPost.objects.filter(
            ticket_id=self.global_ticket_id).select_related().order_by('-id')

        return [ticket for ticket in all_posts_from_ticket]

    def _get_latest_user_ticket(self):
        """
        У администратора и пользователя разная нумерация тикетов. Метод получает последйни
            id тикета во внутренней нумерации пользователя, чтобы id следующего тикета был n+1.
        """
        try:
            latest_user_ticket = Ticket.objects.filter(author_id=self.user_id).latest('user_ticket_id').user_ticket_id
            return latest_user_ticket
        except:
            return 0

    def create_ticket_post(self, ticket_post_text, ticket_id):
        TicketPost(text=ticket_post_text, author_id=self.user_id, ticket_id=ticket_id).save()

    def create_ticket(self, ticket_post_text):
        latest_user_ticket = self._get_latest_user_ticket()
        new_ticket = Ticket(status='pending', author_id=self.user_id, user_ticket_id=latest_user_ticket + 1)

        new_ticket.save()
        ticket_id = new_ticket.id

        self.create_ticket_post(ticket_post_text, ticket_id)

    def is_new_data(self):
        if self.request.POST:
            return True

    def get_global_ticket_id(self):
        """
        У администратора и пользователя разная нумерация тикетов. Админ видит глобальный ID, а пользователь -
            персональный. Например, если у пользователя 3 тикета, он видит Тикет #1, Тикет #2, Тикет #3.
            У администратора они же будут отображаться как Тикет #553, Тикет #579, Тикет #864 и т.д.
        Для некоторых задач, например, для закрытия тикета, удобно получить глобальный id, чтобы
            использовать один и тот же код для администратора и пользователя. Дополнительно, нужно убедиться,
            является ли пользователь создателем тикета.
        """
        if self.is_staff:
            self.global_ticket_id = self.ticket_id
        else:
            ticket = Ticket.objects.get(author_id=self.user_id, user_ticket_id=self.ticket_id)
            self.global_ticket_id = ticket.id
            if self.user_id == ticket.author_id:
                self.is_ticket_owner = True

    def add_new_data_to_database(self):
        if 'new_ticket' in self.post_data:
            self.create_ticket(self.post_data['ticket_post_text'])
        else:
            self.create_ticket_post(self.post_data['ticket_post_text'], self.global_ticket_id)

    def close_ticket(self):
        if self.is_staff or self.is_ticket_owner:
            Ticket.objects.filter(id=self.global_ticket_id).update(status='closed', closed=timezone.now())


@login_required
def new_ticket_page(request):
    user_data = SiteUser(request.user)
    ticket_engine = TicketEngine(request)
    tickets_list = ticket_engine.get_tickets_list()

    if ticket_engine.is_new_data():
        ticket_engine.add_new_data_to_database()

    context = {
        'all_tickets': tickets_list,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance
    }

    return render(request, 'main/ticket/add_new_ticket.html', context)

@login_required
def get_posts_from_ticket(request, ticket_id):
    user_data = SiteUser(request.user)
    ticket_engine = TicketEngine(request, ticket_id)
    tickets_list = ticket_engine.get_tickets_list()

    if not tickets_list:
        return HttpResponseNotFound('Страница не найдена')

    ticket_engine.get_global_ticket_id()

    if ticket_engine.is_new_data():
        ticket_engine.add_new_data_to_database()

    all_posts_from_ticket = ticket_engine.get_posts_from_ticket()

    current_ticket = all_posts_from_ticket[0].ticket
    ticket_status = current_ticket.status

    context = {
        'all_tickets': tickets_list,
        'all_ticket_posts': all_posts_from_ticket,
        'ticket_status': ticket_status,
        'is_staff': ticket_engine.is_staff,
        'ticket_id': ticket_id,
        'orders': user_data.orders,
        'keywords_ordered': user_data.ordered_keywords,
        'balance': user_data.balance,
    }

    return render(request, 'main/ticket/ticket.html', context)


@login_required
def close_ticket(request, ticket_id):
    ticket_engine = TicketEngine(request, ticket_id)

    ticket_engine.get_global_ticket_id()
    ticket_engine.close_ticket()

    return get_posts_from_ticket(request, ticket_id)
