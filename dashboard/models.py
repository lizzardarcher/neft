from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import default
from datetime import datetime


class Brigade(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название бригады')
    description = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Описание')
    customer = models.CharField(max_length=200, blank=True, null=True, verbose_name='Заказчик')
    notes = models.TextField(max_length=4000, blank=True, null=True, verbose_name='Дополнительные примечания')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


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

    def delete(self, *args, **kwargs):
        # удаляем файл из хранилища при удалении записи
        storage = self.file.storage
        name = self.file.name
        super().delete(*args, **kwargs)
        if name and storage.exists(name):
            storage.delete(name)

class WorkerDocument(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название документа", null=False, blank=False)
    file = models.FileField(upload_to='documents/', verbose_name="Файл", null=False, blank=False )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ работников"
        verbose_name_plural = "Документы работников"
        ordering = ['title']

    def delete(self, *args, **kwargs):
        # удаляем файл из хранилища при удалении записи
        storage = self.file.storage
        name = self.file.name
        super().delete(*args, **kwargs)
        if name and storage.exists(name):
            storage.delete(name)

class Manufacturer(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название производителя')

    def __str__(self):
        return self.name


class Equipment(models.Model):
    CONDITION = (('work', 'Рабочее'), ('faulty', 'Неисправное'), ('repair', 'В ремонте'))

    serial = models.CharField(max_length=200, null=False, blank=False, verbose_name='Серийный номер')
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, verbose_name='Категория')
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=False, verbose_name='Бригада')
    documents = models.ManyToManyField(Document, blank=True, verbose_name='Документы для оборудования')
    date_release = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True, verbose_name='Дата выпуска')
    date_exploitation = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True, verbose_name='Дата ввода в эксплуатацию')
    condition = models.CharField(max_length=100, null=False, blank=False, default='work', choices=CONDITION, verbose_name='Состояние оборудования')
    manufacturer = models.CharField(max_length=200, null=True, blank=True, default='', verbose_name='Изготовитель')
    certificate_start = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True, default=None, verbose_name='Дата начала сертификата')
    certificate_end = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True, default=None, verbose_name='Дата окончания сертификата')

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['serial']),
            models.Index(fields=['brigade']),
            models.Index(fields=['category']),
            models.Index(fields=['condition']),
            models.Index(fields=['brigade', 'category']),
        ]
        unique_together = ['serial', 'manufacturer', 'category']


class BrigadeEquipmentRequirement(models.Model):
    brigade = models.ForeignKey(Brigade, on_delete=models.CASCADE, related_name='brigade_requirement')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='brigade_category')
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('brigade', 'category')
        verbose_name = "Требование оборудования бригады"
        verbose_name_plural = "Требования оборудования бригад"
        indexes = [
            models.Index(fields=['brigade']),
            models.Index(fields=['category']),
            models.Index(fields=['brigade', 'category']),
        ]

    def __str__(self):
        return f"{self.brigade.name} требует {self.quantity} ед. из категории '{self.category.name}'"


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
    from_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='transfers_from')
    to_brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='transfers_to')
    transfer_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers')

    def __str__(self):
        return f"{self.equipment} from {self.from_brigade if self.from_brigade else 'Неизвестно'} to {self.to_brigade}"

    class Meta:
        indexes = [
            models.Index(fields=['transfer_date']),
            models.Index(fields=['from_brigade']),
            models.Index(fields=['to_brigade']),
            models.Index(fields=['equipment']),
        ]


class UserActionLog(models.Model):
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    father_name = models.CharField(max_length=200, default='', blank=True, null=True, verbose_name='Отчество')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Должность')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Номер телефона')
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Бригада')
    brigade_start_date = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True,
                                          verbose_name='Дата начала работы в бригаде')
    brigade_end_date = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True,
                                        verbose_name='Дата окончания работы в бригаде')
    is_driver = models.BooleanField(default=False, null=True, blank=True, verbose_name='Водитель')
    status = models.BooleanField(default=True, null=True, blank=True, verbose_name='Отпуск или работа')
    notes = models.TextField(default='', null=True, blank=True, verbose_name='Примечания')

    def __str__(self):
        return self.user.username

    class Meta:
        indexes = [
            models.Index(fields=['brigade']),
            models.Index(fields=['is_driver']),
        ]


### DEPRECATED / DO NOT USE
class WorkTypes(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False,
                            choices=[('Y', 'Обычная работа (Я)'), ('G', 'Работа по геологии (Г)'),
                                     ('O', 'Обслуживание (О)'), ('S', 'Работа стажера (С)')],
                            verbose_name='Название работы')

    def __str__(self):
        return self.name


class WorkerActivity(models.Model):
    WORKER_ACTIVITY_CHOICES = [
        ('Y', 'Обычная работа (Я)'),
        ('G', 'Работа по геологии (Г)'),
        ('O', 'Обслуживание (О)'),
        ('S', 'Работа стажера (С)'),
        ('T', 'Техдежурство (Т)'),
        ('D', 'Дежурство (Д)'),
        ('N', 'Наставничество (Н)'),
        ('-', 'Удалить активность 🛑'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Бригада')
    date = models.DateField(auto_now_add=False, auto_now=False, null=False, blank=False, verbose_name='Дата')
    work_type = models.CharField(max_length=1, null=False, blank=False, default='', choices=WORKER_ACTIVITY_CHOICES,
                                 verbose_name='Тип работы')

    def __str__(self):
        return f'{self.user.username} - {self.brigade} - {self.date} - {self.work_type}'

    class Meta:
        unique_together = ['user', 'date', 'brigade']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['user']),
            models.Index(fields=['brigade']),
            models.Index(fields=['date', 'brigade']),
            models.Index(fields=['date', 'user']),
        ]


class WorkObject(models.Model):
    hole = models.CharField(max_length=200, unique=False, null=False, blank=False, default='',
                            verbose_name='№ Скважины')
    name = models.CharField(max_length=200, unique=False, null=False, blank=False, verbose_name='Месторождение')
    short_name = models.CharField(max_length=200, unique=False, null=False, blank=False, verbose_name='№ куста')
    is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name='Активно')

    def __str__(self):
        return f'{self.short_name} / {self.hole}'

    class Meta:
        verbose_name = 'Месторождение'
        verbose_name_plural = 'Месторождения'
        unique_together = ['hole', 'name', 'short_name']


class BrigadeActivity(models.Model):
    BRIGADE_ACTIVITY_CHOICES = [
        ('(ЗБС) Бурение', '(ЗБС) Бурение'),
        ('(ЗБС) бурение горизонта', '(ЗБС) бурение горизонта'),
        ('(ЗБС) шаблонирование + ГИС', '(ЗБС) шаблонирование + ГИС'),
        ('(ЗБС) спуск хвостовика', '(ЗБС) спуск хвостовика'),
        ('(ВНС) бурение кондуктора', '(ВНС) бурение кондуктора'),
        ('(ВНС) бурение ЭК', '(ВНС) бурение ЭК'),
        ('(ВНС) бурение горизонта', '(ВНС) бурение горизонта'),
        ('(ВНС) спуск хвостовика', '(ВНС) спуск хвостовика'),
        ('Переезд', 'Переезд'),
        ('Простой', 'Простой'),
        ('Авария', 'Авария'),
        ('Движка', 'Движка'),
        ('-', 'Удалить активность 🛑'),
    ]
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Бригада')
    date = models.DateField(auto_now_add=False, auto_now=False, null=False, blank=False, verbose_name='Дата')
    work_type = models.CharField(max_length=100, null=False, blank=False, default='', choices=BRIGADE_ACTIVITY_CHOICES,
                                 verbose_name='Тип работы')
    work_object = models.ForeignKey(WorkObject, on_delete=models.SET_NULL, null=True, blank=True, default='',
                                    verbose_name='Объект работы')
    workers = models.ManyToManyField(User, blank=True,  default=None, verbose_name='Работники')

    def __str__(self):
        return self.brigade.name

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['brigade']),
            models.Index(fields=['date', 'brigade']),
        ]


class OtherCategory(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название категории')

    def __str__(self):
        return self.name


class OtherEquipment(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False, verbose_name='Название оборудования')
    category = models.ForeignKey(OtherCategory, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                 verbose_name='Категория')
    amount = models.IntegerField(null=False, blank=False, default=1, verbose_name='Количество')

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        ordering = ['name']

class Vehicle(models.Model):
    brand = models.CharField(max_length=200, null=False, blank=False, verbose_name='Марка')
    model = models.CharField(max_length=200, null=True, blank=True, verbose_name='Модель')
    number = models.CharField(max_length=200, null=True, blank=True, verbose_name='Гос Номер')

    def __str__(self):
        return f'{self.brand} - {self.model} - {self.number}'

    class Meta:
        unique_together = ['brand', 'model', 'number']


class VehicleMovement(models.Model):
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Водитель')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Автомобиль')
    brigade_from = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Из бригады', related_name='vehicle_movements_from')
    brigade_to = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='В бригаду',
                                   related_name='vehicle_movements_to')
    date = models.DateField(auto_now_add=False, auto_now=False, null=False, blank=False, verbose_name='Дата')
    equipment = models.ManyToManyField(OtherEquipment, blank=True,  default=None, verbose_name='Оборудование')

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['driver']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['brigade_from']),
            models.Index(fields=['brigade_to']),
            models.Index(fields=['date', 'brigade_from']),
            models.Index(fields=['date', 'brigade_to']),
        ]
        # unique_together = ['driver', 'vehicle', 'date', 'brigade_from', 'brigade_to']

class VehicleMovementEquipment(models.Model):
    vehicle_movement = models.ForeignKey(VehicleMovement, on_delete=models.CASCADE)
    equipment = models.ForeignKey(OtherEquipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    comment = models.TextField(null=True, blank=True, default='', verbose_name='Комментарий')
    class Meta:
        # unique_together = ('vehicle_movement', 'equipment')
        ordering = ['equipment']
    def __str__(self):
        return f'{self.equipment.name} ({self.quantity})'


class BrigadeDataFolderQuerySet(models.QuerySet):
    """Кастомный QuerySet для сортировки папок по датам"""
    
    def order_by_date(self, reverse=True):
        """
        Сортирует папки по дате, извлеченной из folder_name (формат ДД.ММ.ГГ)
        reverse=True: от новой к старой (по умолчанию)
        reverse=False: от старой к новой
        """
        def parse_folder_name_to_date(folder_name):
            """Парсит строку ДД.ММ.ГГ в объект datetime"""
            try:
                parts = folder_name.split('.')
                if len(parts) == 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    # Преобразуем ГГ в ГГГГ (26 -> 2026, 99 -> 1999, 00 -> 2000)
                    if year < 50:
                        year += 2000
                    else:
                        year += 1900
                    return datetime(year, month, day)
            except (ValueError, IndexError):
                # Если не удалось распарсить, возвращаем минимальную дату
                return datetime.min
            return datetime.min
        
        # Получаем все объекты и сортируем в Python
        folders = list(self.all())
        folders.sort(key=lambda x: parse_folder_name_to_date(x.folder_name), reverse=reverse)
        return folders


class BrigadeDataFolderManager(models.Manager):
    """Кастомный менеджер для BrigadeDataFolder"""
    
    def get_queryset(self):
        return BrigadeDataFolderQuerySet(self.model, using=self._db)
    
    def order_by_date(self, reverse=True):
        return self.get_queryset().order_by_date(reverse=reverse)


class BrigadeDataFolder(models.Model):
    """Папка для хранения баз данных бригад по датам"""
    folder_name = models.CharField(
        max_length=50,
        verbose_name="Название папки (дата)",
        unique=True,
        help_text="Формат: ДД.ММ.ГГ, например: 02.02.26"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Создал"
    )
    
    # Используем кастомный менеджер
    objects = BrigadeDataFolderManager()

    class Meta:
        verbose_name = "Папка баз данных"
        verbose_name_plural = "Папки баз данных"
        # Убираем ordering из Meta, так как будем использовать кастомную сортировку
        ordering = []

    def __str__(self):
        return self.folder_name

    def delete(self, *args, **kwargs):
        """Удаление папки со всеми файлами"""
        # Удаляем все файлы в папке перед удалением самой папки
        for file_obj in self.files.all():
            # Вызываем метод delete() модели BrigadeDataFile, который удалит физический файл
            file_obj.delete()
        # Удаляем саму папку
        super().delete(*args, **kwargs)


class BrigadeDataFile(models.Model):
    """Файл базы данных, загруженный бригадой"""
    folder = models.ForeignKey(
        BrigadeDataFolder,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Папка"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Название файла",
        null=False,
        blank=False
    )
    file = models.FileField(
        upload_to='brigade_data/%Y/%m/',
        verbose_name="Файл",
        null=False,
        blank=False
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Загрузил"
    )
    brigade = models.ForeignKey(
        Brigade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Бригада"
    )

    class Meta:
        verbose_name = "Файл базы данных"
        verbose_name_plural = "Файлы баз данных"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.folder.folder_name} - {self.title}"

    def delete(self, *args, **kwargs):
        """Удаление файла с физическим удалением с сервера"""
        storage = self.file.storage
        name = self.file.name
        # Сохраняем имя файла перед удалением записи
        if name and storage.exists(name):
            # Удаляем физический файл
            storage.delete(name)
        # Удаляем запись из БД
        super().delete(*args, **kwargs)