from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import price_history_view, edit_user, delete_user, create_user, manage_users

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('calculations/', views.calculations_list, name='calculations_list'),
    path('calculations/create/', views.create_calculation, name='create_calculation'),
    path('calculations/<int:pk>/', views.calculation_detail, name='calculation_detail'),
    path('price-history/', price_history_view, name='price_history'),
    path('users/', manage_users, name='manage_users'),
    path('users/create/', create_user, name='create_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('login/', auth_views.LoginView.as_view(template_name='trades/login.html'), name='login'),
    # Например, можно добавить logout
    path('logout/', auth_views.LogoutView.as_view(template_name='trades/logout.html'), name='logout'),
    path('download-template/', views.download_import_template, name='download_import_template'),
]
