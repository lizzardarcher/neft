from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.models import Brigade, Category, Equipment


class BrigadeListView(LoginRequiredMixin, SuccessMessageMixin, View):
    model = Brigade
    context_object_name = 'brigades'
    template_name = 'dashboard/brigades/brigade_list.html'
    paginate_by = 10

    def get(self, request):
        search_query = request.GET.get('search', '')
        if search_query:
            brigades = Brigade.objects.filter(name__icontains=search_query)
        else:
            brigades = Brigade.objects.all()

        paginator = Paginator(brigades, self.paginate_by)
        page = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)

        context = {'brigades': page_obj}
        return render(request, self.template_name, context)


class BrigadeDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BrigadeDetailView, self).get_context_data(**kwargs)
        context['equipments'] = Equipment.objects.filter(brigade=self.get_object())
        return context

class BrigadeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    ...


class BrigadeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    ...


class BrigadeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    ...
