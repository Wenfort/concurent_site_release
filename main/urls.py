from django.urls import path

from . import views
from .user_logic import user_logic
from .ticket_logic import ticket_logic

urlpatterns = [
    path('balance', user_logic.balance, name='balance'),
    path('registration', user_logic.registration, name='registration'),
    path('authorization', user_logic.authorization, name='authorization'),
    path('logout', user_logic.logout, name='logout'),
    path('change_region', user_logic.change_region, name='change_region'),
    path('change_password', user_logic.change_password, name='change_password'),
    path('password_reset', user_logic.password_reset, name='password_reset'),

    path('tickets/<int:ticket_id>', ticket_logic.get_ticket_posts_from_ticket, name='posts_from_ticket'),
    path('tickets', ticket_logic.get_ticket_posts_from_ticket, name='posts_from_latest_ticket'),
    path('tickets/admin/<int:ticket_id>', ticket_logic.tickets_admin_view, name='ticket_admin_view'),
    path('tickets/admin', ticket_logic.tickets_admin_view, name='ticket_admin_view'),
    path('add_new_ticket', ticket_logic.add_new_ticket, name='add_new_ticket'),
    path('close_ticket/<int:ticket_id>', ticket_logic.close_ticket, name='close_ticket'),

    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('orders', views.get_orders_page, name='get_orders_page'),
    path('orders/<int:order_id>', views.requests_from_order, name='requests_from_order'),
    path('user_confirmation', views.user_confirmation, name='user_confirmation'),
    path('handle_new_request', views.handle_new_request, name='handle_new_request'),
]