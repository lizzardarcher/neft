from django import template
from django.utils.safestring import mark_safe
import os

register = template.Library()


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