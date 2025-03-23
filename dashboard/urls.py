# dashboard/urls.py
from django.urls import path
from .views import index, reports, users, brigades, transfers, categories, equipment

urlpatterns = [
    path('', index.DashboardView.as_view(), name='dashboard'),
    path('instructions', index.InstructionView.as_view(), name='instructions'),

    path('brigades/', brigades.BrigadeListView.as_view(), name='brigade_list'),
    path('brigade_index/<int:pk>', brigades.BrigadeIndexView.as_view(), name='brigade_index'),
    path('brigade/<int:pk>/equipment', brigades.BrigadeDetailView.as_view(), name='brigade_detail'),
    path('brigade/<int:pk>/staff', brigades.BrigadeStaffView.as_view(), name='brigade_staff'),
    path('brigade/brigade_table_total/', brigades.BrigadeTableTotalView.as_view(), name='brigade_table_total'),
    path('brigade/<int:pk>/work/<int:month>/<int:year>/', brigades.BrigadeWorkView.as_view(), name='brigade_work'),
    path('brigade/<int:brigade_id>/brigade_activity_create/', brigades.brigade_activity_create, name='brigade_activity_create'),
    path('brigades/create/', brigades.BrigadeCreateView.as_view(), name='brigade_create'),
    path('brigades/<int:pk>/update/', brigades.BrigadeUpdateView.as_view(), name='brigade_update'),
    path('brigades/<int:pk>/brigade_update_from_work/<int:month>/<int:year>/', brigades.BrigadeUpdateFromWorkView.as_view(), name='brigade_update_from_work'),
    path('brigades/<int:pk>/brigade_update_from_total/', brigades.BrigadeUpdateFromTotalView.as_view(), name='brigade_update_from_total'),
    path('brigades/<int:brigade_id>/delete/', brigades.brigade_delete, name='brigade_delete'),
    path('brigades/object_create/', brigades.work_object_create, name='work_object_create'),
    path('brigades/<int:pk>/work_object_update', brigades.WorkObjectUpdateView.as_view(), name='work_object_update'),
    path('brigades/<int:work_object_id>/work_object_delete', brigades.work_object_delete, name='work_object_delete'),


    path('categories/', categories.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', categories.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', categories.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:category_id>/delete/', categories.CategoryDeleteView.as_view(), name='category_delete'),

    path('equipment/', equipment.EquipmentListView.as_view(), name='equipment_list'),
    path('document/', equipment.DocumentListView.as_view(), name='document_list'),
    path('equipment/create/', equipment.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:brigade_id>/create/', equipment.EquipmentCreateByBrigadeIdView.as_view(),
         name='equipment_create_by_brigade'),
    path('equipment/<int:equipment_id>/<int:brigade_id>/add_document/', equipment.EquipmentAddDocumentsView.as_view(),
         name='equipment_add_document'),
    path('document/<int:document_id>/delete/', equipment.document_delete, name='document_delete'),
    path('equipment/<int:pk>/update/', equipment.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<int:pk>/<int:brigade_id>/update_by_brigade/', equipment.EquipmentUpdateByBrigadeView.as_view(),
         name='equipment_update_by_brigade'),
    path('equipment/<int:equipment_id>/delete/', equipment.equipment_delete, name='equipment_delete'),
    path('equipment/<int:pk>/', equipment.EquipmentDetailView.as_view(), name='equipment_detail'),

    path('manufacturer_delete/<int:manufacturer_id>/', equipment.manufacturer_delete, name='manufacturer_delete'),

    path('transfers/history/', transfers.TransferHistoryView.as_view(), name='transfer_history'),
    path('transfer/vehicle_list', transfers.VehicleListView.as_view(), name='vehicle_list'),
    path('transfer/vehicle_create', transfers.VehicleCreateView.as_view(), name='vehicle_create'),
    path('transfer/vehicle_update/<int:pk>', transfers.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('transfer/vehicle_delete/<int:pk>', transfers.vehicle_delete, name='vehicle_delete'),
    path('transfer/vehicle_detail/<int:pk>', transfers.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('transfer/vehicle_movement_create', transfers.VehicleMovementCreateView.as_view(), name='vehicle_movement_create'),
    path('transfer/vehicle_movement_update/<int:pk>', transfers.VehicleMovementUpdateView.as_view(), name='vehicle_movement_update'),
    path('transfer/vehicle_movement_delete/<int:pk>', transfers.vehicle_movement_delete, name='vehicle_movement_delete'),
    path('transfer/vehicle_movement_detail/<int:pk>', transfers.VehicleMovementDetailView.as_view(), name='vehicle_movement_detail'),
    path('transfer/vehicle_movement_list', transfers.VehicleMovementListView.as_view(), name='vehicle_movement_list'),
    path('transfer/other_category_list', transfers.OtherCategoryListView.as_view(), name='other_category_list'),
    path('transfer/other_category_create', transfers.OtherCategoryCreateView.as_view(), name='other_category_create'),
    path('transfer/other_category_update/<int:pk>', transfers.OtherCategoryUpdateView.as_view(), name='other_category_update'),
    path('transfer/other_category_delete/<int:pk>', transfers.other_category_delete, name='other_category_delete'),
    path('transfer/other_category_detail/<int:pk>', transfers.OtherCategoryDetailView.as_view(), name='other_category_detail'),
    path('transfer/other_equipment_list', transfers.OtherEquipmentListView.as_view(), name='other_equipment_list'),
    path('transfer/other_equipment_create', transfers.OtherEquipmentCreateView.as_view(), name='other_equipment_create'),
    path('transfer/other_equipment_update/<int:pk>', transfers.OtherEquipmentUpdateView.as_view(), name='other_equipment_update'),
    path('transfer/other_equipment_delete/<int:pk>', transfers.other_equipment_delete, name='other_equipment_delete'),
    path('transfer/other_equipment_detail/<int:pk>', transfers.OtherEquipmentDetailView.as_view(), name='other_equipment_detail'),


    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/create/', users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', users.UserUpdateView.as_view(), name='user_update'),
    path('users/staff/<int:pk>/update/', users.UserStaffUpdateView.as_view(), name='user_staff_update'),
    path('user/<int:pk>/update/', users.UserAccountUpdateView.as_view(), name='account_update'),
    path('users/<int:user_id>/delete/', users.user_delete, name='user_delete'),
    path('user/<int:pk>/detail', users.UserDetailView.as_view(), name='user_detail'),
    path('user/update_by_brigade/<int:pk>/<int:brigade_id>/', users.UserUpdateByBrigadeView.as_view(), name='user_update_by_brigade'),
    path('user/worker_activity_create/', users.WorkerActivityCreateView.as_view(), name='worker_activity_create'),
    path('user/user_worker_activity_create/', users.create_worker_activity, name='user_worker_activity_create'),
    path('action-log/', users.UserActionLogView.as_view(), name='user_action_log'),
    path('staff_table_total', users.StaffTableTotalView.as_view(), name='staff_table_total'),

    path('groups/', users.GroupListView.as_view(), name='group_list'),
    path('groups/create/', users.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', users.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', users.GroupDeleteView.as_view(), name='group_delete'),

    path('get_locations/', brigades.get_locations, name='get_locations'),

    path('reports/', reports.ReportListView.as_view(), name='report_list'),
    path('reports/summary/', reports.ReportSummaryView.as_view(), name='report_summary'),
    path('reports/brigades/', reports.ReportByBrigadeView.as_view(), name='report_by_brigade'),

    path('brigade/export/csv/', index.BrigadeCSVExportView.as_view(), name='brigade_export_csv'),
    path('brigade/export/excel/', index.BrigadeExcelExportView.as_view(), name='brigade_export_excel'),

    path('brigade/activity/excel', index.BrigadeActivityExcelView.as_view(), name='brigade_activity_excel'),
    path('user/activity/excel', index.WorkerActivityExcelView.as_view(), name='worker_activity_excel'),

    path('equipment/export/csv/', index.EquipmentCSVExportView.as_view(), name='equipment_export_csv'),
    path('equipment/export/excel/', index.EquipmentExcelExportView.as_view(), name='equipment_export_excel'),


]
