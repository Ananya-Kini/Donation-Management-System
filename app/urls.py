from django.urls import path
from . import views

app_name = 'app'  

urlpatterns = [
    path('', views.home, name='home'),
    path('donor/register/', views.donor_register, name='donor_register'),
    path('donor/login/', views.donor_login, name='donor_login'),
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('fieldworker/register/', views.fieldworker_register, name='fieldworker_register'),
    path('fieldworker/login/', views.fieldworker_login, name='fieldworker_login'),
    path('fieldworker/dashboard/', views.fieldworker_dashboard, name='fieldworker_dashboard'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('sponsorship/create/', views.create_sponsorship, name='create_sponsorship'),
    path('donate_clothes/', views.donate_clothes, name='donate_clothes'), 
    path('fieldworker/create_child/', views.create_child, name='create_child'),
    path('fieldworker/delete_inventory_item/', views.delete_inventory_item, name='delete_inventory_item'),
    path('change_password/', views.change_password, name='change_password'),
]