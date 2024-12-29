from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.detail import SingleObjectMixin

from dashboard.forms import EquipmentCreateByBrigadeForm, EquipmentAddDocumentsForm, DocumentForm
from dashboard.models import Equipment, Brigade, Document


class EquipmentListView(ListView):
    model = Equipment
    context_object_name = 'equipments'
    template_name = 'dashboard/equipment/equipment_list.html'
    paginate_by = 100

    def get_queryset(self):
        """Поиск по названию категории"""
        queryset = super().get_queryset().order_by('name')
        search_request = self.request.GET.get("search")
        if search_request:
            equipment_by_name = Equipment.objects.filter(name__icontains=search_request)
            equipment_by_serial = Equipment.objects.filter(name__icontains=search_request)
            queryset = (equipment_by_name | equipment_by_serial).order_by('name')
        return queryset


class EquipmentCreateView(CreateView):
    ...


class EquipmentCreateByBrigadeIdView(CreateView):
    model = Equipment
    form_class = EquipmentCreateByBrigadeForm
    template_name = 'dashboard/equipment/equipment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brigade'] = Brigade.objects.get(pk=self.kwargs['brigade_id'])
        return context

    def form_valid(self, form):
        brigade_id = self.kwargs.get('brigade_id')
        brigade = get_object_or_404(Brigade, pk=brigade_id)
        form.instance.brigade = brigade
        return super().form_valid(form)

    def get_success_url(self):
        brigade_id = self.kwargs.get('brigade_id')
        return reverse('brigade_detail', args=[brigade_id])


class EquipmentAddDocumentsView(CreateView):
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



class EquipmentUpdateView(UpdateView):
    ...


class EquipmentDeleteView(DeleteView):
    ...

class EquipmentDetailView(DetailView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'dashboard/equipment/equipment_detail.html'
