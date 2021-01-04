from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.publish_request_info, name='publish_request_info'),
    path('add', views.add_new_requests_to_queue, name='add_new_requests_to_queue'),
]