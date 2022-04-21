from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path(r'users/', views.user_directory, name = 'users'),
    path(r'getuserdetails/', views.get_user_details, name = 'getuserdetails'),
    path(r'employeemanagement/', views.admin_employee_management, name = 'employeemanagement'),
    path(r'getemployeedetails/', views.get_employee_details, name = 'getemployeedetails'),
    path(r'insertemployeedetails/', views.insert_employee_details, name = 'insertemployeedetails'),
    path(r'updateemployeedetails/', views.update_employee_details, name = 'updateemployeedetails'),
    path(r'deleteemployeedetails/', views.delete_employee_details, name = 'deleteemployeedetails'),
]
