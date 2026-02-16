from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.http import HttpResponseForbidden, FileResponse
import os

from dashboard.models import BrigadeDataFile, BrigadeDataFolder, Brigade
from dashboard.forms import BrigadeDataFileForm, BrigadeDataFolderForm


def is_manager_or_admin(user):
    """Проверка, является ли пользователь руководителем или администратором"""
    if user.is_superuser:
        return True
    # Проверка через группы (нужно настроить группу "Руководитель")
    return user.groups.filter(name__in=['Руководитель', 'Администратор']).exists() or user.is_staff


def is_regular_worker(user):
    """Проверка, является ли пользователь обычным работником"""
    return user.username == '2' or (hasattr(user, 'profile') and not is_manager_or_admin(user))


@login_required
def brigade_data_list(request):
    """
    Список папок и файлов
    - Обычные работники: видят только папки, могут загружать
    - Руководители: видят всё, могут управлять
    """
    from datetime import datetime
    
    folders = BrigadeDataFolder.objects.all().prefetch_related('files')
    
    # Получаем текущий год в формате ГГ (например, 26 для 2026)
    current_year = datetime.now().strftime('%y')
    
    # Фильтрация по месяцу/году (формат: ММ.ГГ, например 02.26)
    month_filter = request.GET.get('month', None)
    
    # Если фильтр не указан, показываем папки за текущий год
    if not month_filter:
        # Фильтруем папки, которые заканчиваются на текущий год
        folders = folders.filter(folder_name__endswith=current_year)
    else:
        # Фильтруем папки по указанному месяцу/году
        folders = folders.filter(folder_name__endswith=month_filter)
    
    # Получаем список уникальных месяцев/лет для фильтра
    all_folders = BrigadeDataFolder.objects.all()
    months_years = set()
    for folder in all_folders:
        # Извлекаем месяц и год из формата ДД.ММ.ГГ
        parts = folder.folder_name.split('.')
        if len(parts) == 3:
            month_year = f"{parts[1]}.{parts[2]}"  # ММ.ГГ
            months_years.add(month_year)
    
    # Сортируем месяцы/годы в обратном порядке (новые сначала)
    months_years = sorted(months_years, reverse=True)
    
    context = {
        'folders': folders,
        'is_manager': is_manager_or_admin(request.user),
        'is_worker': is_regular_worker(request.user),
        'months_years': months_years,
        'current_month': month_filter,
    }
    return render(request, 'dashboard/brigade_data/data_list.html', context)


@login_required
def brigade_data_upload(request):
    """
    Загрузка файла
    - Доступна для обычных работников и руководителей
    - Обычные работники: могут выбирать бригаду и загружать
    - Руководители: могут выбирать папку и бригаду, загружать
    """
    if request.method == 'POST':
        form = BrigadeDataFileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file_obj = form.save(commit=False)
            
            # Устанавливаем uploaded_by для всех пользователей
            if not file_obj.uploaded_by:
                file_obj.uploaded_by = request.user
            
            file_obj.save()
            messages.success(request, 'Файл успешно загружен!')
            return redirect('brigade_data_list')
    else:
        form = BrigadeDataFileForm(user=request.user)
        # Для обычных работников показываем только активные папки
        if is_regular_worker(request.user) and not is_manager_or_admin(request.user):
            form.fields['folder'].queryset = BrigadeDataFolder.objects.all().order_by('-folder_name')
    
    context = {
        'form': form,
        'is_manager': is_manager_or_admin(request.user),
    }
    return render(request, 'dashboard/brigade_data/data_upload.html', context)


@login_required
def brigade_data_download(request, file_id):
    """
    Скачивание файла
    - Только для руководителей
    """
    if not is_manager_or_admin(request.user):
        return HttpResponseForbidden("У вас нет прав для скачивания файлов")
    
    file_obj = get_object_or_404(BrigadeDataFile, id=file_id)
    
    if file_obj.file:
        try:
            response = FileResponse(
                file_obj.file.open('rb'),
                content_type='application/octet-stream'
            )
            filename = os.path.basename(file_obj.file.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            messages.error(request, f'Ошибка при скачивании файла: {e}')
            return redirect('brigade_data_list')
    
    messages.error(request, 'Файл не найден')
    return redirect('brigade_data_list')


@login_required
def brigade_data_delete(request, file_id):
    """
    Удаление файла
    - Только для руководителей
    """
    if not is_manager_or_admin(request.user):
        return HttpResponseForbidden("У вас нет прав для удаления файлов")
    
    file_obj = get_object_or_404(BrigadeDataFile, id=file_id)
    file_obj.delete()
    messages.success(request, 'Файл успешно удален!')
    return redirect('brigade_data_list')


@login_required
def brigade_data_folder_create(request):
    """
    Создание папки
    - Только для руководителей
    """
    if not is_manager_or_admin(request.user):
        return HttpResponseForbidden("У вас нет прав для создания папок")
    
    if request.method == 'POST':
        form = BrigadeDataFolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.created_by = request.user
            folder.save()
            messages.success(request, f'Папка "{folder.folder_name}" успешно создана!')
            return redirect('brigade_data_list')
    else:
        form = BrigadeDataFolderForm()
    
    return render(request, 'dashboard/brigade_data/folder_create.html', {'form': form})


@login_required
def brigade_data_folder_delete(request, folder_id):
    """
    Удаление папки со всеми файлами
    - Только для руководителей
    """
    if not is_manager_or_admin(request.user):
        return HttpResponseForbidden("У вас нет прав для удаления папок")
    
    folder = get_object_or_404(BrigadeDataFolder, id=folder_id)
    folder_name = folder.folder_name
    folder.delete()  # Каскадное удаление файлов через модель
    messages.success(request, f'Папка "{folder_name}" и все файлы в ней удалены!')
    return redirect('brigade_data_list')

