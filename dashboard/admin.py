from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import *

admin.site.site_header = "Админ Панель"
admin.site.site_title = "rusgeolog.ru"
admin.site.index_title = "rusgeolog.ru Админ Панель"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...

@admin.register(Brigade)
class BrigadeAdmin(admin.ModelAdmin):
    ...

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    ...

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    ...

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    ...

@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'action_time', 'object_id', 'content_type', 'content_object', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ...

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    ...

@admin.register(WorkerActivity)
class WorkerActivityAdmin(admin.ModelAdmin):
    ...

@admin.register(WorkObject)
class WorkObjectAdmin(admin.ModelAdmin):
    ...

@admin.register(BrigadeActivity)
class BrigadeActivityAdmin(admin.ModelAdmin):
    ...

