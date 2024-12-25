from django.db import models
from django.contrib.auth.models import AbstractUser


class Brigade(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название бригады')
    description = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название категории')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    description = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        if self.parent:
            return f"{self.name}/{self.parent}"
        return self.name


class Document(models.Model):
    file = models.FileField(upload_to='equipment_documents/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.upload_date.strftime('%Y-%m-%d %H:%M')})"


class Equipment(models.Model):
    serial = models.CharField(max_length=200, unique=True, verbose_name='Идентификатор оборудования')
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    current_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Бригада')
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Transfer(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    from_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from')
    to_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    transfer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment} from {self.from_brigade if self.from_brigade else 'Неизвестно'} to {self.to_brigade}"


# class User(AbstractUser):
#     ROLE_CHOICES = [
#         ('admin', 'Администратор'),
#         ('operator', 'Оператор'),
#     ]
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator', verbose_name='Права доступа')
#
#     def __str__(self):
#         return self.username
