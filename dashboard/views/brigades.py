from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import  get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.forms import BrigadeForm
from dashboard.models import Brigade, Equipment


class BrigadeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Brigade
    context_object_name = 'brigades'
    template_name = 'dashboard/brigades/brigade_list.html'
    paginate_by = 30

    def get_queryset(self):
        """Поиск по имени и описанию бригады"""
        queryset = super().get_queryset()
        search_request = self.request.GET.get("search")
        if search_request:
            brigade_by_name = Brigade.objects.filter(name__icontains=search_request)
            brigade_by_description = Brigade.objects.filter(description__icontains=search_request)
            queryset = brigade_by_description | brigade_by_name
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_size'] = self.request.GET.get('page_size', self.paginate_by)
        return context

class BrigadeDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_detail.html'

    def get_context_data(self, **kwargs):
        equipments = Equipment.objects.filter(brigade=self.get_object())
        search_request = self.request.GET.get("search")
        category = self.request.GET.get("category")
        sort_by = self.request.GET.get('sort_by', 'id')  # по умолчанию сортируем по id
        order = self.request.GET.get('order', 'asc')  # по умолчанию прямой порядок

        if search_request:
            equipment_by_name = Equipment.objects.filter(brigade=self.get_object(), name__icontains=search_request)
            equipment_by_serial = Equipment.objects.filter(brigade=self.get_object(), serial__icontains=search_request)
            equipments = (equipment_by_name | equipment_by_serial)

        if category:
            equipments = equipments.filter(category__name=category)

        if sort_by:
            if order == 'desc':
                sort_by = f"-{sort_by}"  # ставим минус, если обратный порядок
                equipments = equipments.order_by(sort_by)
            else:
                equipments = equipments.order_by(sort_by)

        # Добавляем пагинацию
        paginator = Paginator(equipments, 10)  # 10 элементов на странице
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = super().get_context_data(**kwargs)
        context['equipments'] = page_obj
        context['page_obj'] = page_obj
        return context

class BrigadeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_create.html'
    form_class = BrigadeForm
    success_url = '/dashboard/brigades'
    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно создана!"

class BrigadeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_update.html'
    form_class = BrigadeForm
    success_url = '/dashboard/brigades'

    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно обновлена!"


def brigade_delete(request, brigade_id):
    brigade = get_object_or_404(Brigade, id=brigade_id)
    brigade.delete()
    messages.success(request, 'Бригада успешно удалена!')
    return redirect('brigade_list')



