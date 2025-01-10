from django.utils import timezone
from .models import UserActionLog, Equipment, Category
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import resolve


class UserActionLoggerMiddleware:
    """Мидлвер для записи действий пользователя."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.method == "POST":
            try:
                url_name = resolve(request.path_info).url_name
            except:
                url_name = "other"

            log = UserActionLog(user=request.user, action_type=f"Запрос {request.method} по url {url_name}")

            if "equipment_update" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='equipment')
                object_id = resolve(request.path_info).kwargs.get('pk')
                log.description = f'Обновлены данные оборудования: {Equipment.objects.get(pk=object_id)}'
            if "equipment_create" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='equipment')
                object_id = resolve(request.path_info).kwargs.get('equipment') or request.POST.get('equipment')
                log.description = f'Добавлено новое оборудование'
            if "equipment_add_document" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='equipment')
                object_id = resolve(request.path_info).kwargs.get('equipment_id')
                log.description = f'Добавлен новый документ'
            if "equipment_delete" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='equipment')
                object_id = resolve(request.path_info).kwargs.get('equipment_id')
                log.description = f'Удалено оборудование'

            if "category_update" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='category')
                object_id = resolve(request.path_info).kwargs.get('pk')
                log.description = f'Обновлены данные категории: {Category.objects.get(pk=object_id)}'
            if "category_create" in url_name:
                log.content_type = ContentType.objects.get(app_label='dashboard', model='category')
                object_id = resolve(request.path_info).kwargs.get('category') or request.POST.get('category')
                log.description = f'Добавлена новая категория'

            try:
                log.object_id = object_id
            except:
                pass
            log.save()

        return response
