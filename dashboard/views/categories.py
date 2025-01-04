from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from dashboard.models import Category, Equipment


class CategoryListView(ListView):
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

class CategoryCreateView(CreateView):
    ...


class CategoryUpdateView(UpdateView):
    ...


class CategoryDeleteView(DeleteView):
    ...