from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path(r'', views.home, name = 'home'),
    path(r'login/', views.login, name = 'login'),
    path(r'logout/', views.logout, name = 'logout'),
    path(r'profile/', views.profile, name = 'profile'),
    path(r'updateprofiledetails/', views.updateprofiledetails, name = 'updateprofiledetails'),
    path(r'users/', views.user_directory, name = 'users'),
    path(r'getuserdetails/', views.get_user_details, name = 'getuserdetails'),

    # employee management
    path(r'employeemanagement/', views.admin_employee_management, name = 'employeemanagement'),
    path(r'getemployeedetails/', views.get_employee_details, name = 'getemployeedetails'),
    path(r'insertemployeedetails/', views.insert_employee_details, name = 'insertemployeedetails'),
    path(r'updateemployeedetails/', views.update_employee_details, name = 'updateemployeedetails'),
    path(r'deleteemployeedetails/', views.delete_employee_details, name = 'deleteemployeedetails'),

    #union details
    path(r'unionmanagement/', views.admin_union_management, name = 'unionemanagement'),
    path(r'getuniondetails/', views.get_union_details, name = 'getuniondetails'),
    path(r'insertuniondetails/', views.insert_union_details, name = 'insertuniondetails'),
    path(r'updateuniondetails/', views.update_union_details, name = 'updateuniondetails'),
    path(r'deleteuniondetails/', views.delete_union_details, name = 'deleteuniondetails'),


    #model management
    path(r'modelmanagement/', views.admin_model_management, name = 'modelmanagement'),
    path(r'getmodeldetails/', views.get_model_details, name = 'getmodeldetails'),
    path(r'insertmodeldetails/', views.insert_model_details, name = 'insertmodeldetails'),
    path(r'updatemodeldetails/', views.update_model_details, name = 'updatemodeldetails'),
    path(r'deletemodeldetails/', views.delete_model_details, name = 'deletemodeldetails'),
    path(r'insertexpertdetails/', views.insert_expert_details, name = 'insertexpertdetails'),

    #airplane management
    path(r'airplanemanagement/', views.admin_airplane_management, name = 'airplanemanagement'),
    path(r'getairplanedetails/', views.get_airplane_details, name = 'getairplanedetails'),
    path(r'insertairplanedetails/', views.insert_airplane_details, name = 'insertairplanedetails'),
    path(r'updateairplanedetails/', views.update_airplane_details, name = 'updateairplanedetails'),
    path(r'deleteairplanedetails/', views.delete_airplane_details, name = 'deleteairplanedetails'),

    # dynamic dropdown values
    path(r'dropdown/', views.dropdown, name = 'dropdown'),    

    # traffic controllers
    path(r'stationmanagement/', views.station_management, name = 'stationmanagement'),
    path(r'getstationdetails/', views.get_station_details, name = 'getstationdetails'),
    path(r'updatestation/', views.update_station_details, name = 'updatestationdetails'),

    # faa admin
    path(r'airworthymanagement/', views.airworthy_management, name = 'airworthymanagement'),
    path(r'getairworthydetails/', views.get_airworthy_details, name = 'getairworthydetails'),
    path(r'updateairworthy/', views.update_airworthy_details, name = 'updateairworthydetails'),

]
