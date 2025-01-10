from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse

from dashboard.forms import CategoryCreateViewForm
from dashboard.models import Category, Equipment


class CategoryListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'dashboard/categories/category_list.html'
    paginate_by = 30

    def get_queryset(self):
        """Поиск по названию категории"""
        queryset = super().get_queryset().order_by('name')
        search_request = self.request.GET.get("search")
        if search_request:
            category_by_name = Category.objects.filter(name__icontains=search_request)
            category_by_parent = Category.objects.filter(name__icontains=search_request)
            category_by_description = Category.objects.filter(description__icontains=search_request)
            queryset = (category_by_description | category_by_name | category_by_parent).order_by('name')
        return queryset

    def get_context_data(self, **kwargs):
        """Отображает список всех категорий с количеством оборудования."""
        categories = Category.objects.filter(parent=None)

        # Подготавливаем словарь с количеством оборудования для каждой категории
        category_counts = {}
        for category in categories:
            def get_all_subcategories(category):
                subcategories = [category]
                for sub in category.subcategories.all():
                    subcategories.extend(get_all_subcategories(sub))
                return subcategories

            all_categories = get_all_subcategories(category)
            category_counts[category.id] = Equipment.objects.filter(category__in=all_categories).count()
        context = super().get_context_data()
        context["category_counts"] = category_counts
        return context

class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryCreateViewForm
    template_name = 'dashboard/categories/category_form.html'

    def get_success_message(self, cleaned_data):
        msg = cleaned_data['name']
        return f'Категория {msg} успешно добавлена!'

    def get_success_url(self):
        return reverse('category_list')

class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryCreateViewForm
    template_name = 'dashboard/categories/category_form.html'

    def get_success_message(self, cleaned_data):
        msg = cleaned_data['name']
        return f'Категория {msg} успешно обновлена!'

    def get_success_url(self):
        return reverse('category_list')


class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    ...


def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Оборудование успешно удалено!')
    return redirect('category_list')
