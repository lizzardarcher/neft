from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, Count, F, Case, When, Value, IntegerField, ExpressionWrapper, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse

from dashboard.forms import CategoryCreateViewForm
from dashboard.mixins import StaffOnlyMixin
from dashboard.models import Category, BrigadeEquipmentRequirement


class CategoryListView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'dashboard/categories/category_list.html'

    def get_queryset(self):
        total_required_subquery = BrigadeEquipmentRequirement.objects.filter(
            category=OuterRef('pk')
        ).values('category').annotate(
            total_sum=Sum('quantity')
        ).values('total_sum')[:1]

        queryset = Category.objects.annotate(
            total_required=Coalesce(Subquery(total_required_subquery, output_field=IntegerField()), Value(0)),
            total_actual=Count('equipment', distinct=True)
        ).annotate(
            difference=F('total_actual') - F('total_required'),
            shortage=Case(
                When(difference__lt=0, then=ExpressionWrapper(F('difference') * -1, output_field=IntegerField())), default=Value(0),
                output_field=IntegerField()
            ),
            surplus=Case(
                When(difference__gt=0, then=F('difference')),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('name')

        search_request = self.request.GET.get("search")
        if search_request:
            queryset = queryset.filter(
                Q(name__icontains=search_request) |
                Q(parent__name__icontains=search_request) |
                Q(description__icontains=search_request)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_categories_stats = self.get_queryset().values('total_required', 'total_actual', 'shortage', 'surplus')

        org_plan = sum(item['total_required'] for item in all_categories_stats)
        org_fact = sum(item['total_actual'] for item in all_categories_stats)
        org_shortage = sum(item['shortage'] for item in all_categories_stats)
        org_surplus = sum(item['surplus'] for item in all_categories_stats)

        context['org_plan'] = org_plan
        context['org_fact'] = org_fact
        # Проверяем org_plan, чтобы избежать деления на ноль
        context['org_percentage'] = (org_fact / org_plan * 100) if org_plan > 0 else 0
        context['org_shortage'] = org_shortage
        context['org_surplus'] = org_surplus

        return context



class CategoryCreateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryCreateViewForm
    template_name = 'dashboard/categories/category_form.html'

    def get_success_message(self, cleaned_data):
        msg = cleaned_data['name']
        return f'Категория {msg} успешно добавлена!'

    def get_success_url(self):
        return reverse('category_list')


class CategoryUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryCreateViewForm
    template_name = 'dashboard/categories/category_form.html'

    def get_success_message(self, cleaned_data):
        msg = cleaned_data['name']
        return f'Категория {msg} успешно обновлена!'

    def get_success_url(self):
        return reverse('category_list')


class CategoryDeleteView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, DeleteView):
    ...


def category_delete(request, category_id):
    if not request.user.is_staff:
        return redirect('worker_document_list')

    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Оборудование успешно удалено!')
    return redirect('category_list')
