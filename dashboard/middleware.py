from django.utils import timezone
from .models import UserActionLog
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import resolve


class UserActionLoggerMiddleware:
    """Мидлвер для записи действий пользователя."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.method == "POST" and not isinstance(response, HttpResponse):
            try:
                url_name = resolve(request.path_info).url_name
            except:
                url_name = "other"

            log = UserActionLog(user=request.user, action_type=f"Запрос {request.method} по url {url_name}")

            if "equipment_update" in url_name:
                log.content_type = ContentType.objects.get(app_label='equipment', model='equipment')
                log.object_id = request.POST.get('id')
            if url_name == "equipment_add_document":
                log.content_type = ContentType.objects.get(app_label='equipment', model='equipment')
                log.object_id = request.POST.get('equipment')
            if url_name == "equipment_delete":
                log.content_type = ContentType.objects.get(app_label='equipment', model='equipment')
                log.object_id = resolve(request.path_info).kwargs.get('equipment_id')

            log.save()

        return response
