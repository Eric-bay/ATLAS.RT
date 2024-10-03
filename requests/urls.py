from django.urls import path
from .views import request_list, request_create

urlpatterns = [
    path('', request_list, name='request_list'),
    path('create/', request_create, name='request_create'),

]

