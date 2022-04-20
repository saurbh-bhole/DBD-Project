from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path(r'users/', views.user_directory, name = 'users'),
    path(r'getuserdetails/', views.get_user_details, name = 'getuserdetails'),
]
