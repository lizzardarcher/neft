from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DetailView

from dashboard.models import Transfer, OtherEquipment, OtherCategory, Vehicle, VehicleMovement


class TransferHistoryView(LoginRequiredMixin, ListView):
    """Отображение истории перемещений оборудования."""
    model = Transfer
    template_name = 'dashboard/transfers/transfer_history.html'
    context_object_name = 'transfers'
    paginate_by = 50


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'dashboard/transfers/vehicle_list.html'
    context_object_name = 'vehicles'


class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'dashboard/transfers/vehicle_detail.html'


class VehicleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    fields = ['brand', 'model', 'number']
    template_name = 'dashboard/transfers/vehicle_form.html'


class VehicleUpdateView(LoginRequiredMixin, SuccessMessageMixin,  UpdateView):
    model = Vehicle
    fields = ['brand', 'model', 'number']
    template_name = 'dashboard/transfers/vehicle_form.html'

    def get_success_url(self):
        return reverse('vehicle_list')


def vehicle_delete(request, pk):
    vehicle = Vehicle.objects.get(pk=pk)
    vehicle.delete()
    return reverse('vehicle_list')


class VehicleMovementListView(LoginRequiredMixin, ListView):
    model = VehicleMovement
    template_name = 'dashboard/transfers/vehicle_movement_list.html'
    context_object_name = 'vehicle_movements'


class VehicleMovementDetailView(LoginRequiredMixin, DetailView):
    model = VehicleMovement
    template_name = 'dashboard/transfers/vehicle_movement_detail.html'


class VehicleMovementCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = VehicleMovement
    fields = ['vehicle', 'brigade_from', 'brigade_to', 'date']
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_success_url(self):
        return reverse('vehicle_movement_list')


class VehicleMovementUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = VehicleMovement
    fields = ['vehicle', 'brigade_from', 'brigade_to', 'date']
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_success_url(self):
        return reverse('vehicle_movement_list')


def vehicle_movement_delete(request, pk):
    vehicle_movement = VehicleMovement.objects.get(pk=pk)
    vehicle_movement.delete()
    return reverse('vehicle_movement_list')


class OtherCategoryListView(LoginRequiredMixin, ListView):
    model = OtherCategory
    template_name = 'dashboard/transfers/other_category_list.html'
    context_object_name = 'other_categories'


class OtherCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OtherCategory
    fields = ['name']
    template_name = 'dashboard/transfers/other_category_form.html'

    def get_success_url(self):
        return reverse('other_category_list')


class OtherCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OtherCategory
    fields = ['name']
    template_name = 'dashboard/transfers/other_category_form.html'

    def get_success_url(self):
        return reverse('other_category_list')

    def get_success_message(self, cleaned_data):
        return f'Категория {self.object} успешно обновлена'



def other_category_delete(request, pk):
    other_category = OtherCategory.objects.get(pk=pk)
    other_category.delete()
    return reverse('other_category_list')


class OtherCategoryDetailView(LoginRequiredMixin, DetailView):
    model = OtherCategory
    template_name = 'dashboard/transfers/other_category_detail.html'


class OtherEquipmentListView(LoginRequiredMixin, ListView):
    model = OtherEquipment
    template_name = 'dashboard/transfers/other_equipment_list.html'
    context_object_name = 'other_equipments'



class OtherEquipmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OtherEquipment
    fields = ['name', 'category', 'amount']
    template_name = 'dashboard/transfers/other_equipment_form.html'

    def get_success_url(self):
        return reverse('other_equipment_list')



class OtherEquipmentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OtherEquipment
    fields = ['name', 'category', 'amount']
    template_name = 'dashboard/transfers/other_equipment_form.html'

    def get_success_url(self):
        return reverse('other_equipment_list')


def other_equipment_delete(request, pk):
    other_equipment = OtherEquipment.objects.get(pk=pk)
    other_equipment.delete()
    return reverse('other_equipment_list')


class OtherEquipmentDetailView(LoginRequiredMixin, DetailView):
    model = OtherEquipment
    template_name = 'dashboard/transfers/other_equipment_detail.html'
