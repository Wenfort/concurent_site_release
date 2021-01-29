from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('restricted_results', views.restricted_results, name='publish_restricted_requests_info'),
    path('add', views.add_new_requests_to_queue, name='add_new_requests_to_queue'),
    path('account', views.account, name='account')
]