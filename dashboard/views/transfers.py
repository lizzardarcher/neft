from django.contrib.auth.mixins import LoginRequiredMixin
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


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    fields = ['brand', 'model', 'number']
    template_name = 'dashboard/transfers/vehicle_form.html'


class VehicleUpdateView(LoginRequiredMixin, UpdateView):
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


class VehicleMovementCreateView(LoginRequiredMixin, CreateView):
    model = VehicleMovement
    fields = ['vehicle', 'brigade_from', 'brigade_to', 'date']
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_success_url(self):
        return reverse('vehicle_movement_list')


class VehicleMovementUpdateView(LoginRequiredMixin, UpdateView):
    model = VehicleMovement
    fields = ['vehicle', 'brigade_from', 'brigade_to', 'date']
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_success_url(self):
        return reverse('vehicle_movement_list')


def vehicle_movement_delete(request, pk):
    vehicle_movement = VehicleMovement.objects.get(pk=pk)
    vehicle_movement.delete()
    return reverse('vehicle_movement_list')
