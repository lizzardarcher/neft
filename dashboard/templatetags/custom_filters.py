from itertools import count

from django import template
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
import os

register = template.Library()


@register.filter
def split(value):
    return value.split(' ')


@register.filter
def get_day(value, day):
    return value.get(day.strftime('%m-%Y'), [])


@register.filter
def get_item(dictionary, key):
    """Получает элемент из словаря по ключу."""
    return dictionary.get(key)


@register.filter
def get_filename(filename):
    filename = filename.split('/')[-1]
    return filename


@register.filter
def is_image(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']


@register.filter
def is_pdf(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext == '.pdf'


@register.filter
def is_word(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.doc', '.docx', 'txt', 'md']


@register.filter
def is_excel(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.xls', '.xlsx']


@register.filter(name='add_class')
def add_class(field, class_name):
    return field.as_widget(attrs={"class": class_name})


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Проверяет, принадлежит ли пользователь к указанной группе.
    """
    return user.groups.filter(name=group_name).exists()


@register.filter(name='trunc_slash')
def trunc_slash(value):
    try:
        return str(value).split('/')[-1]
    except:
        return value


@register.filter
def filesize_mb(size_bytes):
    """Преобразует размер файла из байтов в мегабайты."""
    if not size_bytes:
        return "0 MB"
    size_mb = size_bytes / (1024 * 1024)
    return f"{size_mb:.2f} MB"


@register.filter
def get_work_type(value):
    if value == 'Y':
        return 'Я'
    elif value == 'G':
        return 'Г'
    elif value == 'O':
        return 'О'
    elif value == 'S':
        return 'С'
    else:
        return value


@register.filter(name='has_perm_in_group')
def has_perm_in_group(user, perm_code):
    if not user.is_authenticated:
        return False

    app_label, codename = perm_code.split('.')

    try:
        content_type = ContentType.objects.get(app_label=app_label, model=codename.split('_')[1])
        permission = Permission.objects.get(codename=codename, content_type=content_type)

        for group in user.groups.all():
            if permission in group.permissions.all():
                return True  # User's group has the permission

    except (ContentType.DoesNotExist, Permission.DoesNotExist, ValueError) as e:
        pass

    return False

@register.filter(name='range')
def filter_range(end):
   return range(1, end + 1)  # Include the end value


@register.filter
def get_month_name(month_number):
    return {
        '1': "Январь",
        '2': "Февраль",
        '3': "Март",
        '4': "Апрель",
        '5': "Май",
        '6': "Июнь",
        '7': "Июль",
        '8': "Август",
        '9': "Сентябрь",
        '10': "Октябрь",
        '11': "Ноябрь",
        '12': "Декабрь"
    }[month_number]