from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('calculations/', views.calculations_list, name='calculations_list'),
    path('calculations/create/', views.create_calculation, name='create_calculation'),
    path('calculations/<int:pk>/', views.calculation_detail, name='calculation_detail'),
    path('settings/', views.update_settings, name='update_settings'),
]
