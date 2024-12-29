from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.forms import EquipmentCreateByBrigadeForm
from dashboard.models import Equipment, Brigade


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
    template_name = 'dashboard/equipment/equipment_form.html'  # Замените на путь к вашему шаблону

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brigade'] = Brigade.objects.get(pk=self.kwargs['brigade_id'])
        return context

    def form_valid(self, form):
        brigade_id = self.kwargs.get('brigade_id')  # Извлекаем из URL
        brigade = get_object_or_404(Brigade, pk=brigade_id)
        form.instance.brigade = brigade
        return super().form_valid(form)

    def get_success_url(self):
        brigade_id = self.kwargs.get('brigade_id')
        return reverse('brigade_detail', args=[brigade_id])  # Замените на свой URL просмотра категории

class EquipmentUpdateView(UpdateView):
    ...


class EquipmentDeleteView(DeleteView):
    ...

class EquipmentDetailView(DetailView):
    ...