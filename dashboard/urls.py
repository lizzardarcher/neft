# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index.DashboardView.as_view(), name='dashboard'),  # Главная страница дашборда

    path('brigades/', views.brigades.BrigadeListView.as_view(), name='brigade_list'),
    path('brigades/create/', views.brigades.BrigadeCreateView.as_view(), name='brigade_create'),
    path('brigades/<int:brigade_id>/update/', views.brigades.BrigadeUpdateView.as_view(), name='brigade_update'),
    path('brigades/<int:brigade_id>/delete/', views.brigades.BrigadeDeleteView.as_view(), name='brigade_delete'),

    path('categories/', views.categories.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.categories.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:category_id>/update/', views.categories.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:category_id>/delete/', views.categories.CategoryDeleteView.as_view(), name='category_delete'),

    path('equipment/', views.equipment.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', views.equipment.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:equipment_id>/update/', views.equipment.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<int:equipment_id>/delete/', views.equipment.EquipmentDeleteView.as_view(), name='equipment_delete'),
    path('equipment/<int:equipment_id>/', views.equipment.EquipmentDetailView.as_view(), name='equipment_detail'),

    path('transfers/create/', views.transfers.TransferCreateView.as_view(), name='transfer_create'),
    path('transfers/history/', views.transfers.TransferHistoryView.as_view(), name='transfer_history'),

    path('users/', views.users.UserListView.as_view(), name='user_list'),
    path('users/create/', views.users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/update/', views.users.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', views.users.UserDeleteView.as_view(), name='user_delete'),

    path('reports/', views.reports.ReportListView.as_view(), name='report_list'),
    path('reports/summary/', views.reports.ReportSummaryView.as_view(), name='report_summary'),
    path('reports/brigades/', views.reports.ReportByBrigadeView.as_view(), name='report_by_brigade'),

]
