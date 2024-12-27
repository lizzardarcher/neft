from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.models import Equipment


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


class EquipmentUpdateView(UpdateView):
    ...


class EquipmentDeleteView(DeleteView):
    ...

class EquipmentDetailView(DetailView):
    ...