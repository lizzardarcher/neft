# dashboard/urls.py
from django.urls import path
from .views import index, reports, users, brigades, transfers, categories, equipment

urlpatterns = [
    path('', index.DashboardView.as_view(), name='dashboard'),  # Главная страница дашборда

    path('brigades/', brigades.BrigadeListView.as_view(), name='brigade_list'),
    path('brigade/<int:pk>/detail', brigades.BrigadeDetailView.as_view(), name='brigade_detail'),
    path('brigades/create/', brigades.BrigadeCreateView.as_view(), name='brigade_create'),
    path('brigades/<int:pk>/update/', brigades.BrigadeUpdateView.as_view(), name='brigade_update'),
    path('brigades/<int:brigade_id>/delete/', brigades.brigade_delete, name='brigade_delete'),

    path('categories/', categories.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', categories.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:category_id>/update/', categories.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:category_id>/delete/', categories.CategoryDeleteView.as_view(), name='category_delete'),

    path('equipment/', equipment.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', equipment.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:brigade_id>/create/', equipment.EquipmentCreateByBrigadeIdView.as_view(),
         name='equipment_create_by_brigade'),
    path('equipment/<int:equipment_id>/<int:brigade_id>/add_document/', equipment.EquipmentAddDocumentsView.as_view(),
         name='equipment_add_document'),
    path('equipment/<int:pk>/update/', equipment.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<int:pk>/<int:brigade_id>/update_by_brigade/', equipment.EquipmentUpdateByBrigadeView.as_view(),
         name='equipment_update_by_brigade'),
    path('equipment/<int:equipment_id>/delete/', equipment.equipment_delete, name='equipment_delete'),
    path('equipment/<int:pk>/', equipment.EquipmentDetailView.as_view(), name='equipment_detail'),

    path('transfers/create/', transfers.TransferCreateView.as_view(), name='transfer_create'),
    path('transfers/history/', transfers.TransferHistoryView.as_view(), name='transfer_history'),

    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/create/', users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', users.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', users.user_delete, name='user_delete'),
    path('action-log/', users.UserActionLogView.as_view(), name='user_action_log'),

    path('reports/', reports.ReportListView.as_view(), name='report_list'),
    path('reports/summary/', reports.ReportSummaryView.as_view(), name='report_summary'),
    path('reports/brigades/', reports.ReportByBrigadeView.as_view(), name='report_by_brigade'),

]
