# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_index, name='dashboard'),  # Главная страница дашборда
    path('brigades/', views.brigade_list, name='brigade_list'),
    path('brigades/create/', views.brigade_create, name='brigade_create'),
    path('brigades/<int:brigade_id>/update/', views.brigade_update, name='brigade_update'),
    path('brigades/<int:brigade_id>/delete/', views.brigade_delete, name='brigade_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/update/', views.category_update, name='category_update'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:equipment_id>/update/', views.equipment_update, name='equipment_update'),
    path('equipment/<int:equipment_id>/delete/', views.equipment_delete, name='equipment_delete'),
    path('equipment/<int:equipment_id>/', views.equipment_detail, name='equipment_detail'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/history/', views.transfer_history, name='transfer_history'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/update/', views.user_update, name='user_update'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/summary/', views.report_summary, name='report_summary'),
    path('reports/brigades/', views.report_by_brigade, name='report_by_brigade'),

    # Добавьте другие URL для приложения dashboard
]
