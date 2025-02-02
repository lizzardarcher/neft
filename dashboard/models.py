from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Brigade(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название бригады')
    description = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название категории')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    description = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        if self.parent:
            return f"{self.name}/{self.parent}"
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='Название документа')
    file = models.FileField(upload_to='equipment_documents/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.url} ({self.upload_date.strftime('%Y-%m-%d %H:%M')})"


class Equipment(models.Model):
    CONDITION = (('work', 'Рабочее'), ('faulty', 'Неисправное'), ('repair', 'В ремонте'))

    serial = models.CharField(max_length=200, null=False, blank=False, verbose_name='Серийный номер')
    name = models.CharField(max_length=200, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, verbose_name='Категория')
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=False, verbose_name='Бригада')
    documents = models.ManyToManyField(Document, blank=True, verbose_name='Документы для оборудования')
    date_release = models.DateField(auto_now_add=False, auto_now=False, null=False, blank=False,
                                    verbose_name='Дата выпуска')
    date_exploitation = models.DateField(auto_now_add=False, auto_now=False, null=False, blank=False,
                                         verbose_name='Дата ввода в эксплуатацию')
    condition = models.CharField(max_length=100, null=False, blank=False, default='work', choices=CONDITION,
                                 verbose_name='Состояние оборудования')
    manufacturer = models.CharField(max_length=200, null=False, blank=False, default='', verbose_name='Изготовитель')

    def __str__(self):
        return f"{self.name} ({self.category})"


@receiver(pre_save, sender=Equipment)
def equipment_pre_save(sender, instance, **kwargs):
    """
    Ловим pre_save сигнал для модели equipment, и сохраняем данные о перемещении оборудования в модель Transfers
    """
    if instance.pk:
        old_instance = Equipment.objects.get(pk=instance.pk)
        if old_instance.brigade != instance.brigade:
            Transfer.objects.create(
                equipment=instance,
                from_brigade=old_instance.brigade,
                to_brigade=instance.brigade,
            )



class Transfer(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    from_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from')
    to_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    transfer_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers')

    def __str__(self):
        return f"{self.equipment} from {self.from_brigade if self.from_brigade else 'Неизвестно'} to {self.to_brigade}"


class UserActionLog(models.Model):
    """Модель для хранения истории действий пользователя."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    action_type = models.CharField(max_length=255, verbose_name='Тип действия')
    action_time = models.DateTimeField(auto_now_add=True, verbose_name='Время действия')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def str(self):
        return f'{self.user} - {self.action_type} - {self.action_time.strftime("%Y-%m-%d %H:%M:%S")}'

    class Meta:
        verbose_name = 'История действий пользователя'
        verbose_name_plural = 'История действий пользователей'
