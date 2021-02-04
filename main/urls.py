from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('add', views.add_new_requests_to_queue, name='add_new_requests_to_queue'),
    path('orders', views.get_orders_page, name='get_orders_page'),
    path('balance', views.balance, name='balance'),
    path('ordered_requests', views.ordered_requests, name='ordered_requests')
]