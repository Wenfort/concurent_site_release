from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from main.models import TicketPost, Ticket
from main.user_logic.user_logic import SiteUser

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

    def create_ticket_post(self, user_ticket_id, ticket_post_text):
        ticket_id = self.choose_ticket(user_ticket_id).ticket_id
        TicketPost(ticket_id=ticket_id,
                   ticket_post_author_id=self.user_id,
                   ticket_post_text=ticket_post_text,
                   ticket_post_order=0,
                   ).save()

    def create_ticket(self, request):
        post_request = request.POST

        all_user_tickets = self.get_all_user_tickets()
        try:
            latest_user_ticket_id = all_user_tickets.latest('user_ticket_id').user_ticket_id
        except:
            latest_user_ticket_id = 0


        ticket = Ticket(author_id=self.user_id,
                        user_ticket_id=latest_user_ticket_id +1,
                        status='pending', )
        ticket.save()
        self.create_ticket_post(ticket.user_ticket_id, post_request['ticket_post_text'])

        return HttpResponseRedirect('/tickets')

    def choose_ticket(self, ticket_id=None):
        if ticket_id:
            if self.user_role == 'admin':
                ticket = self.all_tickets.get(ticket_id=ticket_id)
            else:
                ticket = self.all_tickets.get(user_ticket_id=ticket_id)
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


def add_new_ticket(request):
    user_data = SiteUser(request.account_data.id)
    tickets_data = Tickets(user_data)

    if request.account_data.is_staff:
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


def tickets_admin_view(request, ticket_id=None):
    user_data = SiteUser(request.user)
    tickets_data = Tickets(user_data)
    all_tickets = tickets_data.get_all_admin_tickets()

    if all_tickets:
        choosen_ticket = tickets_data.choose_ticket(ticket_id)
        if request.method == "POST":
            post_request = request.POST

            if ticket_id == None:
                ticket_id = choosen_ticket.user_ticket_id

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
        return add_new_ticket(request)


def get_ticket_posts_from_ticket(request, ticket_id=None):
    if request.user.is_staff:
        return HttpResponseRedirect('/tickets/admin')

    user_data = SiteUser(request.account_data.id)
    tickets_data = Tickets(user_data)

    all_tickets = tickets_data.get_all_user_tickets()

    if all_tickets:
        choosen_ticket = tickets_data.choose_ticket(ticket_id)
        if choosen_ticket:
            if request.method == "POST":
                post_request = request.POST

                if ticket_id == None:
                    ticket_id = choosen_ticket.user_ticket_id

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


def close_ticket(request, ticket_id):
    user_data = SiteUser(request.account_data.id)
    ticket_data = Tickets(user_data)

    return ticket_data.close_ticket(ticket_id)