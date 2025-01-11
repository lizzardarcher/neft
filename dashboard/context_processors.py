from django.conf import settings

def debug_mode(request):
    """Передает значение DEBUG в контекст всех шаблонов."""
    return {'debug_mode': settings.DEBUG}
