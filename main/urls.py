from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('orders', views.get_orders_page, name='get_orders_page'),
    path('orders/<int:order_id>', views.requests_from_order, name='requests_from_order'),
    path('balance', views.balance, name='balance'),
    path('registration', views.registration, name='registration'),
    path('authorization', views.authorization, name='authorization'),
    path('tickets', views.tickets, name='tickets'),
    path('add_new_ticket', views.add_new_ticket, name='add_new_ticket'),
]