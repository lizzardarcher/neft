from django.conf import settings
import psutil


def debug_mode(request):
    """Передает значение DEBUG в контекст всех шаблонов."""
    return {'debug_mode': settings.DEBUG}


def disk_space_info(request):
    """
    Возвращает информацию о свободном месте на диске для использования в шаблонах.
    """
    try:
        disk = psutil.disk_usage('/')  # '/' - корневой диск, можно изменить на нужный
        free_gb = disk.free / (1024 ** 3)  # Преобразуем в гигабайты
        total_gb = disk.total / (1024 ** 3)  # Общий объем
        used_gb = disk.used / (1024 ** 3)  # Использовано
        percent_used = disk.percent
        return {
            'disk_free_gb': round(free_gb, 2),
            'disk_total_gb': round(total_gb, 2),
            'disk_used_gb': round(used_gb, 2),
            'disk_percent_used': percent_used,
            'disk_chart_data': {
                'percent_used': percent_used,
                'free_gb': round(free_gb, 2),
                'used_gb': round(used_gb, 2),
                'total_gb': round(total_gb, 2),
            }
        }
    except Exception as e:
        #  Обработка ошибок, например, если psutil не может получить информацию.
        print(f"Ошибка получения информации о диске: {e}")
        return {
            'disk_free_gb': 'N/A',
            'disk_total_gb': 'N/A',
            'disk_used_gb': 'N/A',
            'disk_percent_used': 'N/A',
        }
