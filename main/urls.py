from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='publish_results'),
    path('add', views.add_new_requests_to_queue, name='add_new_requests_to_queue'),
    path('orders', views.get_orders_page, name='get_orders_page'),
]