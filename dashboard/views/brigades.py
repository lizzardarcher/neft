from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.forms import BrigadeForm
from dashboard.models import Brigade, Category, Equipment


class BrigadeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Brigade
    context_object_name = 'brigades'
    template_name = 'dashboard/brigades/brigade_list.html'
    paginate_by = 10

    def get_queryset(self):
        """Поиск по имени и описанию бригады"""
        search_request = self.request.GET.get("search")
        if search_request:
            brigade_by_name = Brigade.objects.filter(name__icontains=search_request)
            brigade_by_description = Brigade.objects.filter(description__icontains=search_request)
            object_list = brigade_by_description | brigade_by_name
        else:
            object_list = Brigade.objects.all()
        return object_list

class BrigadeDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BrigadeDetailView, self).get_context_data(**kwargs)
        context['equipments'] = Equipment.objects.filter(brigade=self.get_object())
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


def brigade_delete(request, brigade_id):
    brigade = get_object_or_404(Brigade, id=brigade_id)
    brigade.delete()
    messages.success(request, 'Бригада успешно удалена!')
    return redirect('brigade_list')
    # return render(request, 'dashboard/brigades/brigade_list.html', {'message': 'Успешно удалено'})