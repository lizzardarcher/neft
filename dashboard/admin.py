from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import *

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
