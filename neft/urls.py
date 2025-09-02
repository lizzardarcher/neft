from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from dashboard.views import users

urlpatterns = [
    path('', include('home.urls')),
    path('', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    # path('admin/', admin.site.urls),
    path('1/', users.document_list, name='worker_document_list'),
    path('worker_document_create/', users.worker_document_create, name='worker_document_create'),
    path('worker_document_delete/<int:pk>', users.worker_document_delete, name='worker_document_delete'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
