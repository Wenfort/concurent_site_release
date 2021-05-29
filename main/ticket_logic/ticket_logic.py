from django.shortcuts import render
from django.utils import timezone
from main.models import TicketPost, Ticket


class TicketEngine:

    def __init__(self, request, ticket_id=0):
        self.request = request
        self.user_id = request.user.id
        self.is_staff = request.user.is_staff
        self.post_data = request.POST
        self.ticket_id = ticket_id

    def get_tickets_list(self):
        if self.is_staff:
            return Ticket.objects.filter()
        else:
            return Ticket.objects.filter(author_id=self.user_id)

    def get_posts_from_ticket(self, user_ticket_id):

        if self.is_staff:
            all_posts_from_ticket = TicketPost.objects.filter(
                ticket_id=user_ticket_id).select_related().order_by('-id')
        else:
            all_posts_from_ticket = TicketPost.objects.filter(
                ticket__user_ticket_id=user_ticket_id).select_related().order_by('-id')

        return [ticket for ticket in all_posts_from_ticket]

    def get_latest_user_ticket(self):
        try:
            latest_user_ticket = Ticket.objects.filter(author_id=self.user_id).latest('user_ticket_id').user_ticket_id
            return latest_user_ticket
        except:
            return 0

    def create_ticket_post(self, ticket_post_text, ticket_id):
        TicketPost(text=ticket_post_text, author_id=self.user_id, ticket_id=ticket_id).save()

    def create_ticket(self, ticket_post_text):
        latest_user_ticket = self.get_latest_user_ticket()
        new_ticket = Ticket(status='pending', author_id=self.user_id, user_ticket_id=latest_user_ticket + 1)

        new_ticket.save()
        ticket_id = new_ticket.id

        self.create_ticket_post(ticket_post_text, ticket_id)

    def is_new_data(self):
        if self.request.POST:
            return True

    def get_global_ticket_id(self):
        if self.is_staff:
            chosen_ticket = Ticket.objects.get(id=self.ticket_id)
        else:
            chosen_ticket = Ticket.objects.get(author_id=self.user_id, user_ticket_id=self.ticket_id)
        return chosen_ticket.id

    def add_new_data_to_database(self):
        if 'new_ticket' in self.post_data:
            self.create_ticket(self.post_data['ticket_post_text'])
        else:
            ticket_id = self.get_global_ticket_id()
            self.create_ticket_post(self.post_data['ticket_post_text'], ticket_id)

    def close_ticket(self):
        if self.is_staff:
            Ticket.objects.filter(id=self.ticket_id).update(status='closed', closed=timezone.now())


def new_ticket_page(request):
    ticket_engine = TicketEngine(request)
    tickets_list = ticket_engine.get_tickets_list()

    if ticket_engine.is_new_data():
        ticket_engine.add_new_data_to_database()

    context = {
        'all_tickets': tickets_list,
    }

    return render(request, 'main/ticket/add_new_ticket.html', context)


def get_posts_from_ticket(request, ticket_id):
    ticket_engine = TicketEngine(request, ticket_id)
    tickets_list = ticket_engine.get_tickets_list()

    if ticket_engine.is_new_data():
        ticket_engine.add_new_data_to_database()

    all_posts_from_ticket = ticket_engine.get_posts_from_ticket(ticket_id)

    current_ticket = all_posts_from_ticket[0].ticket
    ticket_status = current_ticket.status

    context = {
        'all_tickets': tickets_list,
        'all_ticket_posts': all_posts_from_ticket,
        'ticket_status': ticket_status,
        'is_staff': ticket_engine.is_staff,
        'ticket_id': ticket_id,
    }

    return render(request, 'main/ticket/ticket.html', context)


def close_ticket(request, ticket_id):
    ticket_engine = TicketEngine(request, ticket_id)

    ticket_engine.close_ticket()

    return get_posts_from_ticket(request, ticket_id)
