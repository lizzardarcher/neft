from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from dashboard.views import users, brigade_data

urlpatterns = [
    path('', include('home.urls')),
    path('', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    # path('admin/', admin.site.urls),
    path('worker_document_create/', users.worker_document_create, name='worker_document_create'),
    path('worker_document_delete/<int:pk>', users.worker_document_delete, name='worker_document_delete'),

    path('1/', users.document_list, name='worker_document_list'),
    # Ресурс /2 для загрузки баз данных бригад
    path('2/', brigade_data.brigade_data_list, name='brigade_data_list'),
    path('2/upload/', brigade_data.brigade_data_upload, name='brigade_data_upload'),
    path('2/download/<int:file_id>/', brigade_data.brigade_data_download, name='brigade_data_download'),
    path('2/delete/<int:file_id>/', brigade_data.brigade_data_delete, name='brigade_data_delete'),
    path('2/folder/create/', brigade_data.brigade_data_folder_create, name='brigade_data_folder_create'),
    path('2/folder/delete/<int:folder_id>/', brigade_data.brigade_data_folder_delete, name='brigade_data_folder_delete'),

    path('developer/', admin.site.urls),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
