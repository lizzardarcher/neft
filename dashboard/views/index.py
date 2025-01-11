from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import TemplateView, View

from dashboard.models import Brigade, Category, Equipment, UserActionLog, Transfer


class DashboardView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['brigades'] = Brigade.objects.all()
        context['categories'] = Category.objects.all()
        context['equipment'] = Equipment.objects.all()
        context['users'] = User.objects.all()
        context['user_log'] = UserActionLog.objects.all()
        context['transfers'] = Transfer.objects.all()
        return context


class InstructionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Отображает инструкцию в зависимости от группы пользователя."""
    template_name = 'dashboard/instruction.html'

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request):
        user = request.user
        group_names = [group.name for group in user.groups.all()]

        # Разграничение прав и доступных действий для каждой группы
        instructions = {}
        if user.is_superuser:
            instructions['admin'] = self.get_admin_instructions()
            instructions['manager'] = self.get_manager_instructions()
            instructions['operator'] = self.get_operator_instructions()

        elif 'Управляющий' in group_names:
            instructions['manager'] = self.get_manager_instructions()
            instructions['operator'] = self.get_operator_instructions()
        elif 'Оператор' in group_names:
            instructions['operator'] = self.get_operator_instructions()
        else:
            instructions = None

        permissions = self.get_permissions_table(user)
        return render(request, self.template_name, {'instructions': instructions, 'permissions': permissions})

    def get_admin_instructions(self):
        return {
            "Пользователи": [
                "Создание, редактирование и удаление пользователей",
                "Управление группами пользователей",
                "Просмотр истории действий пользователей",
                "Просмотр истории действий (admin)",
            ],
            "Бригады": [
                "Просмотр всех бригад",
                "Создание, редактирование и удаление бригад",
            ],
            "Категории": [
                "Просмотр всех категорий",
                "Создание, редактирование и удаление категорий",
            ],
            "Оборудование": [
                "Просмотр всего оборудования",
                "Создание, редактирование и удаление оборудования",
                "Добавление документов к оборудованию",
            ],
            "Документы": [
                "Просмотр всех документов"
            ]
        }

    def get_manager_instructions(self):
        return {
            "Бригады": [
                "Просмотр всех бригад",
                "Создание, редактирование и удаление бригад",
            ],
            "Категории": [
                "Просмотр всех категорий",
                "Создание, редактирование и удаление категорий",
            ],
            "Оборудование": [
                "Просмотр всего оборудования",
                "Создание, редактирование и удаление оборудования",
                "Добавление документов к оборудованию",
            ],
            "Документы": [
                "Просмотр всех документов"
            ]
        }

    def get_operator_instructions(self):
        return {
            "Категории": [
                "Просмотр всех категорий",
            ],
            "Оборудование": [
                "Просмотр всего оборудования",
                "Редактирование оборудования",
                "Добавление документов к оборудованию",
            ]
        }

    def get_permissions_table(self, user):
        """Формируем таблицу разрешений с emoji."""

        permissions = {
            "Модель": ["Пользователи", "Бригады", "Категории", "Оборудование", "Документы"],
            "Администратор": ["🛑", "✅", "✅", "✅", "✅"],
            "Управляющий": ["🛑", "✅", "✅", "✅", "✅"],
            "Оператор": ["🛑", "🛑", "✅", "✅", "🛑"],
        }
        if user.is_superuser:
            permissions["Администратор"] = ["✅", "✅", "✅", "✅", "✅"]

        return permissions
