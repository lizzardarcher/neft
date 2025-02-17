from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.detail import SingleObjectMixin

from dashboard.forms import EquipmentCreateByBrigadeForm, EquipmentAddDocumentsForm, DocumentForm, EquipmentCreateForm
from dashboard.models import Equipment, Brigade, Document, Manufacturer


class EquipmentListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Equipment
    context_object_name = 'equipments'
    template_name = 'dashboard/equipment/equipment_list.html'
    paginate_by = 50

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all().order_by('name')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_request = self.request.GET.get("search")
        category = self.request.GET.get("category")
        sort_by = self.request.GET.get('sort_by', 'id')  # по умолчанию сортируем по id
        order = self.request.GET.get('order', 'asc')  # по умолчанию прямой порядок
        if search_request:
            equipment_by_name = Equipment.objects.filter(name__icontains=search_request)
            equipment_by_serial = Equipment.objects.filter(name__icontains=search_request)
            queryset = (equipment_by_name | equipment_by_serial)
        if sort_by:
            if order == 'desc':
                sort_by = f"-{sort_by}"  # ставим минус, если обратный порядок
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by(sort_by)
        if category:
            if sort_by:
                queryset = queryset.filter(category__name=category).order_by(f'{sort_by}name')
            else:
                queryset = queryset.filter(category__name=category).order_by(f'name')
        return queryset


class EquipmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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

class EquipmentCreateByBrigadeIdView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class EquipmentAddDocumentsView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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
        return redirect(reverse('equipment_add_document', args=[equipment_id, brigade_id]))


class EquipmentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'dashboard/equipment/equipment_update.html'
    success_message = 'Оборудование успешно обновлено!'

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


class EquipmentUpdateByBrigadeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'dashboard/equipment/equipment_update_by_brigade.html'
    success_message = 'Оборудование успешно обновлено!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['manufacturer'] = Manufacturer.objects.all().order_by('name')
        return context

    def get_success_url(self):
        return  reverse('brigade_detail', args=[self.kwargs.get('brigade_id')])

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


class EquipmentDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'dashboard/equipment/equipment_detail.html'


def equipment_delete(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.delete()
    messages.success(request, 'Оборудование успешно удалено!')
    return redirect('equipment_list')


class DocumentListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
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


