from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:request_name>', views.publish_request_info, name='publish_request_info')
]