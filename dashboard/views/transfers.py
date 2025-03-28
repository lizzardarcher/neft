from datetime import datetime
import calendar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DetailView, TemplateView
from django.shortcuts import render
from django.views import View

from dashboard.forms import VehicleForm, VehicleMovementForm, OtherEquipmentForm, OtherCategoryForm, \
    VehicleMovementEquipmentFormSet, VehicleMovementFilterForm
from dashboard.models import Transfer, OtherEquipment, OtherCategory, Vehicle, VehicleMovement


class TransferHistoryView(LoginRequiredMixin, ListView):
    """Отображение истории перемещений оборудования."""
    model = Transfer
    template_name = 'dashboard/transfers/transfer_history.html'
    context_object_name = 'transfers'
    paginate_by = 50


class TransferIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/transfers/transfers_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_equipment_count'] = OtherEquipment.objects.all().count()
        context['other_category_count'] = OtherCategory.objects.all().count()
        context['vehicle_count'] = Vehicle.objects.all().count()
        context['vehicle_movement_count'] = VehicleMovement.objects.all().count()
        context['year'] = datetime.now().strftime('%Y')
        context['month'] = datetime.now().strftime('%m')
        return context


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'dashboard/transfers/vehicle_list.html'
    context_object_name = 'vehicles'


class VehicleDetailView(LoginRequiredMixin, View):
    template_name = 'dashboard/transfers/vehicle_detail.html'

    RUSSIAN_MONTHS = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
    }

    def get(self, request, pk):
        vehicle = get_object_or_404(Vehicle, pk=pk)
        year = request.GET.get('year')
        month = request.GET.get('month')

        movements = vehicle.vehiclemovement_set.all()

        if year:
            movements = movements.filter(date__year=year)
        if month:
            movements = movements.filter(date__month=month)

        years = VehicleMovement.objects.dates('date', 'year')

        context = {
            'vehicle': vehicle,
            'movements': movements,
            'years': [d.year for d in years],
            'selected_year': year,
            'RUSSIAN_MONTHS': self.RUSSIAN_MONTHS,
            'selected_month': month,
            'months': self.RUSSIAN_MONTHS,  # Use the static dictionary
        }
        return render(request, self.template_name, context)


class VehicleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'dashboard/transfers/vehicle_form.html'

    def get_success_url(self):
        return reverse('vehicle_list')


class VehicleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'dashboard/transfers/vehicle_form.html'

    def get_success_url(self):
        return reverse('vehicle_list')


def vehicle_delete(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    messages.success(request, 'Транспорт успешно удален!')
    return redirect('vehicle_list')


class VehicleMovementListView(LoginRequiredMixin, ListView):
    model = VehicleMovement
    template_name = 'dashboard/transfers/vehicle_movement_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            month = int(self.request.GET.get('month'))
            year = int(self.request.GET.get('year'))
        except:
            month = datetime.now().month
            year = datetime.now().year

        previous_month = month - 1
        next_month = month + 1

        if previous_month < 1:
            previous_month = 12
            previous_year = year - 1
            next_year = year
        elif next_month > 12:
            next_month = 1
            next_year = year + 1
            previous_year = year
        else:
            previous_year = year
            next_year = year

        context['month'] = month
        context['year'] = year
        context['previous_month'] = previous_month
        context['next_month'] = next_month
        context['previous_year'] = previous_year
        context['next_year'] = next_year

        context['vehicle_movements'] = VehicleMovement.objects.filter(date__month=month, date__year=year).order_by(
            'date')
        context['vehicles'] = Vehicle.objects.all().order_by('brand')
        return context


class VehicleMovementTotalListView(LoginRequiredMixin, ListView):
    model = VehicleMovement
    template_name = 'dashboard/transfers/vehicle_movement_list_total.html'
    context_object_name = 'vehicle_movements'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = VehicleMovementFilterForm(self.request.GET)
        if form.is_valid():
            month = form.cleaned_data.get('month')
            year = form.cleaned_data.get('year')

            brigade_from = form.cleaned_data.get('brigade_from')
            brigade_to = form.cleaned_data.get('brigade_to')
            driver = form.cleaned_data.get('driver')
            vehicle = form.cleaned_data.get('vehicle')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if month:
                queryset = queryset.filter(date__month=month)
            if year:
                queryset = queryset.filter(date__year=year)

            if brigade_from:
                queryset = queryset.filter(brigade_from=brigade_from)
            if brigade_to:
                queryset = queryset.filter(brigade_to=brigade_to)
            if driver:
                queryset = queryset.filter(driver=driver)
            if vehicle:
                queryset = queryset.filter(vehicle=vehicle)
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = VehicleMovementFilterForm(self.request.GET)
        queryset = self.get_queryset()
        context['total_movements'] = queryset.count()
        context['movements_by_month'] = queryset.annotate(month_year=TruncMonth('date')).values('month_year').annotate(count=Count('id')).order_by('month_year')
        context['movements_by_brigade_from'] = queryset.values('brigade_from__name').annotate(count=Count('id')).order_by('-count')
        context['movements_by_brigade_to'] = queryset.values('brigade_to__name').annotate(count=Count('id')).order_by('-count')
        context['movements_by_driver'] = queryset.values('driver__last_name', 'driver__first_name').annotate( count=Count('id')).order_by('-count')
        context['movements_by_vehicle'] = queryset.values('vehicle__brand', 'vehicle__model', 'vehicle__number').annotate(count=Count('id')).order_by('-count')

        equipment_summary = {}
        for movement in queryset:
            for equipment_entry in movement.vehiclemovementequipment_set.all():
                equipment_name = equipment_entry.equipment.name
                if equipment_name not in equipment_summary:
                    equipment_summary[equipment_name] = 0
                equipment_summary[equipment_name] += equipment_entry.quantity

        context['equipment_summary'] = equipment_summary
        return context


class VehicleMovementDetailView(LoginRequiredMixin, DetailView):
    model = VehicleMovement
    template_name = 'dashboard/transfers/vehicle_movement_detail.html'


class VehicleMovementCreateView(CreateView):
    model = VehicleMovement
    form_class = VehicleMovementForm
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = VehicleMovementEquipmentFormSet(self.request.POST)
        else:
            context['formset'] = VehicleMovementEquipmentFormSet()
        return context

    def get_success_url(self):
        try:
            month = int(self.request.GET.get('month'))
            year = int(self.request.GET.get('year'))
        except:
            month = datetime.now().month
            year = datetime.now().year
        return reverse('vehicle_movement_list') + f'?month={str(month)}&year={str(year)}'

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class VehicleMovementUpdateView(UpdateView):
    model = VehicleMovement
    form_class = VehicleMovementForm
    template_name = 'dashboard/transfers/vehicle_movement_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle_movement = self.get_object()
        if self.request.POST:
            context['formset'] = VehicleMovementEquipmentFormSet(self.request.POST, instance=vehicle_movement)
        else:
            context['formset'] = VehicleMovementEquipmentFormSet(instance=vehicle_movement)
        return context

    def get_success_url(self):
        try:
            month = int(self.request.GET.get('month'))
            year = int(self.request.GET.get('year'))
        except:
            month = datetime.now().month
            year = datetime.now().year
        return reverse('vehicle_movement_list') + f'?month={str(month)}&year={str(year)}'

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            messages.error(self.request, f"Пожалуйста, исправьте ошибки в форме. {formset.get_form_error()}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


def vehicle_movement_delete(request, pk):
    vehicle_movement = VehicleMovement.objects.get(pk=pk)
    vehicle_movement.delete()
    month = request.GET.get('month')  # Получаем как строку, если None
    year = request.GET.get('year')  # Получаем как строку, если None

    # Используем reverse() для создания URL и добавляем параметры через query string
    url = reverse('vehicle_movement_list')
    if month and year:
        url += f'?month={month}&year={year}'

    return redirect(url)


class OtherCategoryListView(LoginRequiredMixin, ListView):
    model = OtherCategory
    template_name = 'dashboard/transfers/other_category_list.html'
    context_object_name = 'other_categories'


class OtherCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OtherCategory
    form_class = OtherCategoryForm
    template_name = 'dashboard/transfers/other_category_form.html'

    def get_success_url(self):
        return reverse('other_category_list')


class OtherCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OtherCategory
    form_class = OtherCategoryForm
    template_name = 'dashboard/transfers/other_category_form.html'

    def get_success_url(self):
        return reverse('other_category_list')

    def get_success_message(self, cleaned_data):
        return f'Категория {self.object} успешно обновлена'


def other_category_delete(request, pk):
    other_category = OtherCategory.objects.get(pk=pk)
    other_category.delete()
    return redirect('other_category_list')


class OtherCategoryDetailView(LoginRequiredMixin, DetailView):
    model = OtherCategory
    template_name = 'dashboard/transfers/other_category_detail.html'


class OtherEquipmentListView(LoginRequiredMixin, ListView):
    model = OtherEquipment
    template_name = 'dashboard/transfers/other_equipment_list.html'
    context_object_name = 'other_equipments'


class OtherEquipmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OtherEquipment
    form_class = OtherEquipmentForm
    template_name = 'dashboard/transfers/other_equipment_form.html'

    def get_success_url(self):
        return reverse('other_equipment_list')

    def get_success_message(self, cleaned_data):
        return f'Оборудование {self.object} успешно добавлено'


class OtherEquipmentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OtherEquipment
    form_class = OtherEquipmentForm
    template_name = 'dashboard/transfers/other_equipment_form.html'

    def get_success_url(self):
        return reverse('other_equipment_list')

    def get_success_message(self, cleaned_data):
        return f'Оборудование {self.object} успешно обновлено'


def other_equipment_delete(request, pk):
    other_equipment = OtherEquipment.objects.get(pk=pk)
    other_equipment.delete()
    return redirect('other_equipment_list')


class OtherEquipmentDetailView(LoginRequiredMixin, DetailView):
    model = OtherEquipment
    template_name = 'dashboard/transfers/other_equipment_detail.html'
