import io
import os
import zipfile
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from dashboard.forms import EquipmentCreateByBrigadeForm, EquipmentAddDocumentsForm, DocumentForm, EquipmentCreateForm
from dashboard.mixins import StaffOnlyMixin
from dashboard.models import Equipment, Brigade, Document, Manufacturer


class EquipmentListView(LoginRequiredMixin,  StaffOnlyMixin,SuccessMessageMixin, ListView):
    model = Equipment
    context_object_name = 'equipments'
    template_name = 'dashboard/equipment/equipment_list.html'
    paginate_by = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all().order_by('name')
        context['now_date'] = date.today()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        search_request = self.request.GET.get("search", None)
        category = self.request.GET.get("category", None)
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')

        # Фильтрация по поиску одним запросом с Q
        if search_request:
            queryset = queryset.filter(
                Q(name__icontains=search_request) | Q(serial__icontains=search_request)
            )

        # Фильтрация по категории
        if category:
            queryset = queryset.filter(category__name=category)

        # Сортировка
        if sort_by:
            if order == 'desc':
                sort_by = f"-{sort_by}"
            queryset = queryset.order_by(sort_by)

        return queryset


class EquipmentCreateView(LoginRequiredMixin,  StaffOnlyMixin,SuccessMessageMixin, CreateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'dashboard/equipment/equipment_form.html'
    success_message = 'Оборудование успешно добавлено!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['manufacturer'] = Manufacturer.objects.all().order_by('name')
        return context

    def get_success_url(self):
        return reverse('equipment_list')

    def form_valid(self, form):
        manufacturer_id = self.request.POST.get('id_manufacturer')
        new_manufacturer_name = self.request.POST.get('new_manufacturer')

        if new_manufacturer_name:
            form.instance.manufacturer = new_manufacturer_name
            Manufacturer.objects.get_or_create(name=new_manufacturer_name)
        elif manufacturer_id:
            form.instance.manufacturer = manufacturer_id
        return super().form_valid(form)


class EquipmentCreateByBrigadeIdView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, CreateView):
    model = Equipment
    form_class = EquipmentCreateByBrigadeForm
    template_name = 'dashboard/equipment/equipment_form_by_brigade.html'
    success_message = 'Оборудование успешно добавлено!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brigade'] = Brigade.objects.get(pk=self.kwargs['brigade_id'])
        context['manufacturer'] = Manufacturer.objects.all().order_by('name')
        return context

    def form_valid(self, form):
        brigade_id = self.kwargs.get('brigade_id')
        brigade = get_object_or_404(Brigade, pk=brigade_id)
        form.instance.brigade = brigade

        manufacturer_id = self.request.POST.get('id_manufacturer')
        new_manufacturer_name = self.request.POST.get('new_manufacturer')

        if new_manufacturer_name:
            form.instance.manufacturer = new_manufacturer_name
            Manufacturer.objects.get_or_create(name=new_manufacturer_name)
        elif manufacturer_id:
            form.instance.manufacturer = manufacturer_id
        return super().form_valid(form)

    def get_success_url(self):
        brigade_id = self.kwargs.get('brigade_id')
        return reverse('brigade_detail', args=[brigade_id])


class EquipmentAddDocumentsView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, CreateView):
    model = Document
    form_class = EquipmentAddDocumentsForm
    template_name = 'dashboard/equipment/equipment_add_documents.html'

    def get_object(self):
        return get_object_or_404(Equipment, pk=self.kwargs.get('equipment_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment'] = self.get_object()
        context['brigade'] = Brigade.objects.get(pk=self.kwargs.get('brigade_id'))
        context['document_form'] = DocumentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        document_form = DocumentForm(request.POST, request.FILES)
        if document_form.is_valid():
            new_document = document_form.save()
            self.object.documents.add(new_document)
            return self.form_valid(self.get_form())

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        equipment_id = self.kwargs.get('equipment_id')
        brigade_id = self.kwargs.get('brigade_id')
        search_request = self.request.GET.get("search", None)
        category = self.request.GET.get("category", None)
        page = self.request.GET.get("page", 1)
        return redirect(reverse('equipment_add_document', args=[equipment_id, brigade_id])+f'?search={search_request}&page={page}&category={category}')


class EquipmentUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'dashboard/equipment/equipment_update.html'
    success_message = 'Оборудование успешно обновлено!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['manufacturer'] = Manufacturer.objects.all().order_by('name')
        return context

    def get_success_url(self):
        search_request = self.request.GET.get("search")
        category = self.request.GET.get("category")
        page = self.request.GET.get("page", 1)
        return reverse('equipment_list') + f'?search={search_request}&category={category}&page={page}'

    def form_valid(self, form):
        manufacturer_id = self.request.POST.get('id_manufacturer')
        new_manufacturer_name = self.request.POST.get('new_manufacturer')
        if new_manufacturer_name:
            form.instance.manufacturer = new_manufacturer_name
            Manufacturer.objects.get_or_create(name=new_manufacturer_name)
        elif manufacturer_id:
            form.instance.manufacturer = manufacturer_id
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Пожалуйста, исправьте ошибки в форме. {form.errors}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при загрузке формы: {e}")
            return render(request, self.template_name, {'form': EquipmentCreateForm()})

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при отправке формы: {e}")
            return render(request, self.template_name, {
                'form': EquipmentCreateForm(request.POST, instance=self.get_object())})


class EquipmentUpdateByBrigadeView(LoginRequiredMixin,  StaffOnlyMixin,SuccessMessageMixin, UpdateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'dashboard/equipment/equipment_update_by_brigade.html'
    success_message = 'Оборудование успешно обновлено!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['manufacturer'] = Manufacturer.objects.all().order_by('name')
        return context

    def get_success_url(self):
        search_request = self.request.GET.get("search")
        return reverse('brigade_detail', args=[self.kwargs.get('brigade_id')]) + f'?search={search_request or ""}'

    def form_valid(self, form):
        manufacturer_id = self.request.POST.get('id_manufacturer')
        new_manufacturer_name = self.request.POST.get('new_manufacturer')
        if new_manufacturer_name:
            form.instance.manufacturer = new_manufacturer_name
            Manufacturer.objects.get_or_create(name=new_manufacturer_name)
        elif manufacturer_id:
            form.instance.manufacturer = manufacturer_id
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Пожалуйста, исправьте ошибки в форме. {form.errors}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при загрузке формы: {e}")
            return render(request, self.template_name, {'form': EquipmentCreateForm()})

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при отправке формы: {e}")
            return render(request, self.template_name, {
                'form': EquipmentCreateForm(request.POST, instance=self.get_object())
            })


class EquipmentDetailView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, DetailView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'dashboard/equipment/equipment_detail.html'


def equipment_delete(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.delete()
    messages.success(request, 'Оборудование успешно удалено!')
    referer_url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(referer_url)
    # return redirect('equipment_list')


class DocumentListView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, ListView):
    model = Document
    context_object_name = 'documents'
    template_name = 'dashboard/equipment/document_list.html'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        search_request = self.request.GET.get("search")
        title = self.request.GET.get("title")
        sort_by = self.request.GET.get('sort_by', 'title')
        order = self.request.GET.get('order', 'asc')
        if search_request:
            equipment_by_name = Document.objects.filter(title__icontains=search_request)
            queryset = equipment_by_name
        if title:
            queryset = queryset.filter(title=title)
        if sort_by:
            if order == 'desc':
                sort_by = f"-{sort_by}"
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by(sort_by)
        return queryset

def document_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    messages.success(request, 'Документ успешно удален!')
    referer_url = request.META.get('HTTP_REFERER')
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        return redirect('equipment_list')


def manufacturer_delete(request, manufacturer_id):
    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
    manufacturer.delete()
    messages.success(request, 'Изготовитель успешно удален!')
    referer_url = request.META.get('HTTP_REFERER')
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        return redirect('equipment_list')


def download_all_equipment_documents(request, equipment_id):
    """
    Скачивает все документы, связанные с указанным оборудованием, в виде ZIP-архива.
    """
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    documents = equipment.documents.all()

    if not documents.exists():
        return HttpResponse("Для данного оборудования нет связанных документов.", status=404)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for doc in documents:
            if doc.file:
                try:
                    with doc.file.open('rb') as f:
                        file_content = f.read()
                        zipf.writestr(os.path.basename(doc.file.name), file_content)
                except FileNotFoundError:
                    messages.error(request,f"Предупреждение: Файл '{doc.file.name}' не найден на диске для документа '{doc.title}'.")
                except Exception as e:
                    messages.error(request,f"Ошибка при обработке файла '{doc.file.name}': {e}.")
            else:
                messages.error(request,f"Предупреждение: Документ '{doc.title}' не имеет связанного файла.")

    zip_buffer.seek(0)

    file_base_name = f"Документы_{equipment.name}_{equipment.serial}".strip()
    zip_filename = f"{file_base_name}.zip"

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')

    content_disposition = f"attachment; filename*=utf-8''{escape_uri_path(zip_filename)}"
    response['Content-Disposition'] = content_disposition

    return response


def download_all_brigade_documents(request, brigade_id):
    """
    Скачивает все уникальные документы, связанные со всеми единицами оборудования
    указанной бригады, в виде ZIP-архива.
    """
    brigade = get_object_or_404(Brigade, pk=brigade_id)

    unique_documents = {}

    equipment_in_brigade = Equipment.objects.filter(brigade=brigade)

    if not equipment_in_brigade.exists():
        return HttpResponse(f"Для бригады '{brigade.name}' нет привязанного оборудования.", status=404)

    for equipment in equipment_in_brigade:
        for doc in equipment.documents.all():
            unique_documents[doc.pk] = doc

    documents_to_zip = list(unique_documents.values())

    if not documents_to_zip:
        return HttpResponse(f"Для бригады '{brigade.name}' нет связанных документов.", status=404)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for doc in documents_to_zip:
            if doc.file:
                try:
                    with doc.file.open('rb') as f:
                        file_content = f.read()

                        file_extension = os.path.splitext(doc.file.name)[1]
                        internal_zip_filename = f"{doc.title}_{doc.pk}{file_extension}"
                        internal_zip_filename = "".join(x for x in internal_zip_filename if x.isalnum() or x in "._- ")

                        zipf.writestr(internal_zip_filename, file_content)
                except FileNotFoundError:
                    messages.error(request, f"Предупреждение: Файл '{doc.file.name}' не найден на диске для документа '{doc.title}' (ID: {doc.pk}). Пропускаем.")
                except Exception as e:
                    messages.error(request, f"Ошибка при обработке файла '{doc.file.name}' (ID: {doc.pk}): {e}. Пропускаем.")
            else:
                messages.error(request, f"Предупреждение: Документ '{doc.title}' (ID: {doc.pk}) не имеет связанного файла. Пропускаем.")

    zip_buffer.seek(0)

    brigade_name_clean = brigade.name.replace('/', '_').replace('\\', '_').strip()
    zip_filename = f"Документы_Бригада_{brigade_name_clean}.zip"

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f"attachment; filename*=utf-8''{escape_uri_path(zip_filename)}"

    return response