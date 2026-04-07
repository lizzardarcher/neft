from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Brigade, Category, Document, WorkerDocument, Manufacturer, Equipment,
    BrigadeEquipmentRequirement, Transfer, UserActionLog, UserProfile,
    WorkTypes, WorkerActivity, WorkObject, BrigadeActivity,
    OtherCategory, OtherEquipment, Vehicle, VehicleMovement,
    VehicleMovementEquipment, BrigadeDataFolder, BrigadeDataFile
)

# Настройки админ-панели
admin.site.site_header = "Админ Панель - Rusgeolog.ru"
admin.site.site_title = "Rusgeolog.ru Admin"
admin.site.index_title = "Панель управления системой учета оборудования"

# Отменяем стандартную регистрацию User
admin.site.unregister(User)

# ==================== Пользователи ====================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Расширенная админка для пользователей"""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active',
                    'date_joined', 'profile_link')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    date_hierarchy = 'date_joined'
    ordering = ('-date_joined',)

    # Убираем дублирующий fieldset, так как date_joined и last_login уже есть в BaseUserAdmin.fieldsets
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     ('Дополнительная информация', {'fields': ('date_joined', 'last_login')}),
    # )

    def profile_link(self, obj):
        if hasattr(obj, 'profile'):
            url = reverse('admin:dashboard_userprofile_change', args=[obj.profile.pk])
            return format_html('<a href="{}">Профиль</a>', url)
        return "—"

    profile_link.short_description = 'Профиль'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Профили пользователей"""
    list_display = ('user', 'position', 'brigade', 'phone_number', 'is_driver', 'status', 'brigade_start_date',
                    'brigade_end_date')
    list_filter = ('is_driver', 'status', 'brigade', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position', 'phone_number')
    raw_id_fields = ('user', 'brigade')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Личная информация', {
            'fields': ('father_name', 'position', 'phone_number')
        }),
        ('Бригада', {
            'fields': ('brigade', 'brigade_start_date', 'brigade_end_date')
        }),
        ('Дополнительно', {
            'fields': ('is_driver', 'status', 'notes')
        }),
    )


# ==================== Бригады ====================

@admin.register(Brigade)
class BrigadeAdmin(admin.ModelAdmin):
    """Бригады"""
    list_display = ('id', 'name', 'affiliation', 'customer', 'equipment_count', 'staff_count', 'description_short')
    list_filter = ('affiliation', 'customer',)
    search_fields = ('name', 'description', 'customer', 'notes')
    readonly_fields = ('equipment_count', 'staff_count')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'affiliation', 'customer')
        }),
        ('Описание', {
            'fields': ('description', 'notes')
        }),
        ('Статистика', {
            'fields': ('equipment_count', 'staff_count'),
            'classes': ('collapse',)
        }),
    )

    def equipment_count(self, obj):
        return obj.equipment_set.count()

    equipment_count.short_description = 'Количество оборудования'

    def staff_count(self, obj):
        return obj.userprofile_set.count()

    staff_count.short_description = 'Количество сотрудников'

    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return "—"

    description_short.short_description = 'Описание'


# ==================== Категории ====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Категории оборудования"""
    list_display = ('id', 'name', 'parent', 'equipment_count', 'subcategories_count')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    readonly_fields = ('equipment_count', 'subcategories_count')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'parent', 'description')
        }),
        ('Статистика', {
            'fields': ('equipment_count', 'subcategories_count'),
            'classes': ('collapse',)
        }),
    )

    def equipment_count(self, obj):
        return obj.equipment_set.count()

    equipment_count.short_description = 'Количество оборудования'

    def subcategories_count(self, obj):
        return obj.subcategories.count()

    subcategories_count.short_description = 'Подкатегорий'


# ==================== Оборудование ====================

class EquipmentDocumentInline(admin.TabularInline):
    """Встроенная форма для документов оборудования"""
    model = Equipment.documents.through
    extra = 1
    verbose_name = 'Документ'
    verbose_name_plural = 'Документы'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Оборудование"""
    list_display = ('id', 'name', 'serial', 'category', 'brigade', 'condition', 'manufacturer', 'date_release',
                    'certificate_status')
    list_filter = ('condition', 'category', 'brigade', 'manufacturer', 'date_release', 'date_exploitation')
    search_fields = ('name', 'serial', 'manufacturer', 'category__name', 'brigade__name')
    date_hierarchy = 'date_release'
    raw_id_fields = ('category', 'brigade')
    readonly_fields = ('certificate_status',)
    inlines = [EquipmentDocumentInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'serial', 'category', 'brigade', 'manufacturer')
        }),
        ('Состояние', {
            'fields': ('condition',)
        }),
        ('Даты', {
            'fields': ('date_release', 'date_exploitation', 'certificate_start', 'certificate_end')
        }),
        ('Сертификат', {
            'fields': ('certificate_status',),
            'classes': ('collapse',)
        }),
    )

    def certificate_status(self, obj):
        from django.utils import timezone
        if obj.certificate_end:
            if obj.certificate_end < timezone.now().date():
                return format_html('<span style="color: red;">Просрочен</span>')
            elif (obj.certificate_end - timezone.now().date()).days <= 30:
                return format_html('<span style="color: orange;">Скоро истечет</span>')
            else:
                return format_html('<span style="color: green;">Действителен</span>')
        return "—"

    certificate_status.short_description = 'Статус сертификата'


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Производители"""
    list_display = ('id', 'name', 'equipment_count')
    search_fields = ('name',)
    readonly_fields = ('equipment_count',)

    def equipment_count(self, obj):
        return Equipment.objects.filter(manufacturer=obj.name).count()

    equipment_count.short_description = 'Количество оборудования'


# ==================== Документы ====================

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Документы оборудования"""
    list_display = ('id', 'title', 'file_link', 'upload_date', 'equipment_count')
    list_filter = ('upload_date',)
    search_fields = ('title',)
    date_hierarchy = 'upload_date'
    readonly_fields = ('file_link', 'equipment_count', 'upload_date')

    fieldsets = (
        ('Документ', {
            'fields': ('title', 'file', 'file_link')
        }),
        ('Информация', {
            'fields': ('upload_date', 'equipment_count'),
            'classes': ('collapse',)
        }),
    )

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Открыть файл</a>', obj.file.url)
        return "—"

    file_link.short_description = 'Файл'

    def equipment_count(self, obj):
        return obj.equipment_set.count()

    equipment_count.short_description = 'Используется в оборудовании'


@admin.register(WorkerDocument)
class WorkerDocumentAdmin(admin.ModelAdmin):
    """Документы работников"""
    list_display = ('id', 'title', 'file_link', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('file_link', 'uploaded_at')

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Открыть файл</a>', obj.file.url)
        return "—"

    file_link.short_description = 'Файл'


# ==================== Перемещения ====================

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    """Перемещения оборудования"""
    list_display = ('id', 'equipment', 'from_brigade', 'to_brigade', 'transfer_date', 'user')
    list_filter = ('transfer_date', 'from_brigade', 'to_brigade')
    search_fields = ('equipment__name', 'equipment__serial', 'from_brigade__name', 'to_brigade__name', 'user__username')
    date_hierarchy = 'transfer_date'
    raw_id_fields = ('equipment', 'from_brigade', 'to_brigade', 'user')
    readonly_fields = ('transfer_date',)
    ordering = ('-transfer_date',)


# ==================== Требования бригад ====================

@admin.register(BrigadeEquipmentRequirement)
class BrigadeEquipmentRequirementAdmin(admin.ModelAdmin):
    """Требования оборудования бригад"""
    list_display = ('id', 'brigade', 'category', 'quantity', 'actual_count', 'difference')
    list_filter = ('brigade', 'category')
    search_fields = ('brigade__name', 'category__name')
    raw_id_fields = ('brigade', 'category')

    def actual_count(self, obj):
        return Equipment.objects.filter(brigade=obj.brigade, category=obj.category).count()

    actual_count.short_description = 'Фактическое количество'

    def difference(self, obj):
        actual = Equipment.objects.filter(brigade=obj.brigade, category=obj.category).count()
        diff = actual - obj.quantity
        if diff < 0:
            return format_html('<span style="color: red;">-{}</span>', abs(diff))
        elif diff > 0:
            return format_html('<span style="color: green;">+{}</span>', diff)
        return "0"

    difference.short_description = 'Разница'


# ==================== Активности ====================

@admin.register(WorkerActivity)
class WorkerActivityAdmin(admin.ModelAdmin):
    """Активности работников"""
    list_display = ('id', 'user', 'brigade', 'date', 'work_type')
    list_filter = ('work_type', 'brigade', 'date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'brigade__name')
    date_hierarchy = 'date'
    raw_id_fields = ('user', 'brigade')
    ordering = ('-date', 'user')


@admin.register(BrigadeActivity)
class BrigadeActivityAdmin(admin.ModelAdmin):
    """Активности бригад"""
    list_display = ('id', 'brigade', 'date', 'work_type', 'work_object', 'workers_count')
    list_filter = ('work_type', 'brigade', 'date', 'work_object')
    search_fields = ('brigade__name', 'work_object__name', 'work_object__short_name')
    date_hierarchy = 'date'
    raw_id_fields = ('brigade', 'work_object')
    filter_horizontal = ('workers',)
    ordering = ('-date', 'brigade')

    def workers_count(self, obj):
        return obj.workers.count()

    workers_count.short_description = 'Количество работников'


# ==================== Объекты работ ====================

@admin.register(WorkObject)
class WorkObjectAdmin(admin.ModelAdmin):
    """Объекты работ (месторождения)"""
    list_display = ('id', 'short_name', 'hole', 'name', 'is_active', 'activities_count')
    list_filter = ('is_active',)
    search_fields = ('short_name', 'hole', 'name')
    readonly_fields = ('activities_count',)

    def activities_count(self, obj):
        return obj.brigadeactivity_set.count()

    activities_count.short_description = 'Активностей'


# ==================== Транспорт ====================

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Транспортные средства"""
    list_display = ('id', 'brand', 'model', 'number', 'movements_count')
    list_filter = ('brand',)
    search_fields = ('brand', 'model', 'number')
    readonly_fields = ('movements_count',)

    def movements_count(self, obj):
        return obj.vehiclemovement_set.count()

    movements_count.short_description = 'Перемещений'


class VehicleMovementEquipmentInline(admin.TabularInline):
    """Встроенная форма для оборудования в перемещении"""
    model = VehicleMovementEquipment
    extra = 1


@admin.register(VehicleMovement)
class VehicleMovementAdmin(admin.ModelAdmin):
    """Перемещения транспорта"""
    list_display = ('id', 'date', 'driver', 'vehicle', 'brigade_from', 'brigade_to', 'equipment_count')
    list_filter = ('date', 'brigade_from', 'brigade_to', 'vehicle')
    search_fields = ('driver__username', 'driver__first_name', 'driver__last_name', 'vehicle__brand', 'vehicle__model',
                     'vehicle__number')
    date_hierarchy = 'date'
    raw_id_fields = ('driver', 'vehicle', 'brigade_from', 'brigade_to')
    inlines = [VehicleMovementEquipmentInline]
    ordering = ('-date',)

    def equipment_count(self, obj):
        return obj.vehiclemovementequipment_set.count()

    equipment_count.short_description = 'Количество оборудования'


@admin.register(VehicleMovementEquipment)
class VehicleMovementEquipmentAdmin(admin.ModelAdmin):
    """Оборудование в перемещениях транспорта"""
    list_display = ('id', 'vehicle_movement', 'equipment', 'quantity', 'comment')
    list_filter = ('equipment__category',)
    search_fields = ('equipment__name', 'comment', 'vehicle_movement__vehicle__brand')
    raw_id_fields = ('vehicle_movement', 'equipment')


# ==================== Прочее оборудование ====================

@admin.register(OtherCategory)
class OtherCategoryAdmin(admin.ModelAdmin):
    """Категории прочего оборудования"""
    list_display = ('id', 'name', 'equipment_count')
    search_fields = ('name',)
    readonly_fields = ('equipment_count',)

    def equipment_count(self, obj):
        return obj.otherequipment_set.count()

    equipment_count.short_description = 'Количество оборудования'


@admin.register(OtherEquipment)
class OtherEquipmentAdmin(admin.ModelAdmin):
    """Прочее оборудование"""
    list_display = ('id', 'name', 'category', 'amount')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    raw_id_fields = ('category',)


# ==================== Базы данных бригад ====================

@admin.register(BrigadeDataFolder)
class BrigadeDataFolderAdmin(admin.ModelAdmin):
    """Папки баз данных бригад"""
    list_display = ('id', 'folder_name', 'created_by', 'created_at', 'files_count')
    list_filter = ('created_at',)
    search_fields = ('folder_name', 'created_by__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'files_count')
    raw_id_fields = ('created_by',)
    ordering = ('folder_name',)

    fieldsets = (
        ('Информация', {
            'fields': ('folder_name', 'created_by', 'created_at')
        }),
        ('Статистика', {
            'fields': ('files_count',),
            'classes': ('collapse',)
        }),
    )

    def files_count(self, obj):
        return obj.files.count()

    files_count.short_description = 'Количество файлов'


@admin.register(BrigadeDataFile)
class BrigadeDataFileAdmin(admin.ModelAdmin):
    """Файлы баз данных бригад"""
    list_display = ('id', 'title', 'folder', 'brigade', 'uploaded_by', 'uploaded_at', 'file_size', 'file_link')
    list_filter = ('folder', 'brigade', 'uploaded_at')
    search_fields = ('title', 'folder__folder_name', 'brigade__name', 'uploaded_by__username')
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('uploaded_at', 'file_link', 'file_size')
    raw_id_fields = ('folder', 'brigade', 'uploaded_by')
    ordering = ('-uploaded_at',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'folder', 'brigade', 'file')
        }),
        ('Информация о загрузке', {
            'fields': ('uploaded_by', 'uploaded_at', 'file_link', 'file_size'),
            'classes': ('collapse',)
        }),
    )

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Скачать файл</a>', obj.file.url)
        return "—"

    file_link.short_description = 'Файл'

    def file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} Б"
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} КБ"
            else:
                return f"{size / (1024 * 1024):.2f} МБ"
        return "—"

    file_size.short_description = 'Размер файла'


# ==================== Логи ====================

@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    """Логи действий пользователей"""
    list_display = ('id', 'user', 'action_type', 'action_time', 'content_type', 'object_id', 'description_short')
    list_filter = ('action_type', 'content_type', 'action_time')
    search_fields = ('user__username', 'action_type', 'description')
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time',)
    raw_id_fields = ('user', 'content_type')
    ordering = ('-action_time',)

    def description_short(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return "—"

    description_short.short_description = 'Описание'

    def has_add_permission(self, request):
        return False  # Логи создаются автоматически

    def has_change_permission(self, request, obj=None):
        return False  # Логи нельзя изменять


# ==================== Устаревшие модели ====================

@admin.register(WorkTypes)
class WorkTypesAdmin(admin.ModelAdmin):
    """Устаревшая модель - типы работ"""
    list_display = ('id', 'name')
    search_fields = ('name',)

    def has_add_permission(self, request):
        return False  # Модель помечена как DEPRECATED
