from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from dashboard.mixins import StaffOnlyMixin


class ReportsView(LoginRequiredMixin, StaffOnlyMixin, TemplateView):
    template_name = 'dashboard/reports/reports_list.html'
    page_title = 'Отчёты'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title

        # Определяем список отчетов с их описаниями и ссылками
        context['reports'] = [
            {
                'name': 'Статус оснащенности бригады',
                'description': 'Подробный отчет по плану и факту оснащения выбранной бригады по категориям.',
                'url': '{% url "dashboard:brigade_equipment_status_list" %}', # Замените на актуальный URL, если он другой
                'export_url': None, # Отдельный экспорт для каждой бригады, поэтому здесь null
                'requires_selection': True, # Требует выбора бригады
                'selection_url_name': 'dashboard:brigade_equipment_status_list', # URL, где происходит выбор
            },
            {
                'name': 'Выгрузка всех бригад (оснащенность)',
                'description': 'Полный список всех бригад с показателями их оснащенности (План/Факт).',
                'url': '{% url "dashboard:brigade_list" %}', # URL списка бригад
                'export_url': '{% url "dashboard:export_organization_equipment_status_excel" %}',
                'requires_selection': False,
            },
            {
                'name': 'Выгрузка по категориям (оснащенность)',
                'description': 'Общий отчет по оснащенности всех категорий оборудования по всей организации.',
                'url': '{% url "dashboard:category_list" %}', # URL списка категорий
                'export_url': '{% url "dashboard:export_category_equipment_status_excel" %}',
                'requires_selection': False,
            },
            {
                'name': 'Выгрузка всех бригад (данные)',
                'description': 'Список всех бригад с их основными данными (ID, название, заказчик и т.д.).',
                'url': None, # Если нет отдельной страницы для просмотра всех бригад, кроме списка
                'export_url': '{% url "dashboard:brigade_export_excel" %}', # Замените на актуальный URL
                'requires_selection': False,
            },
            {
                'name': 'Выгрузка всего оборудования (данные)',
                'description': 'Полный список всего имеющегося оборудования с его характеристиками.',
                'url': None,  # Если нет отдельной страницы для просмотра всего оборудования
                'export_url': '{% url "dashboard:equipment_export_excel" %}',  # Замените на актуальный URL
                'requires_selection': False,
            },
            {
                'name': 'Активность бригад (за месяц)',
                'description': 'Отчет по активности всех бригад за выбранный месяц и год.',
                'url': None,  # Если нет отдельной страницы для просмотра активности бригад
                'export_url': '{% url "dashboard:brigade_activity_excel" %}?month={{ current_month }}&year={{ current_year }}',
                # Пример с параметрами
                'requires_selection': True,  # Требует выбора месяца/года
                'selection_url_name': 'dashboard:brigade_activity_excel',  # URL, где происходит выбор
                'parameters': ['month', 'year'],
            },
            {
                'name': 'Активность работников (за месяц)',
                'description': 'Отчет по активности всех работников за выбранный месяц и год.',
                'url': None,
                'export_url': '{% url "dashboard:worker_activity_excel" %}?month={{ current_month }}&year={{ current_year }}',
                # Пример с параметрами
                'requires_selection': True,
                'selection_url_name': 'dashboard:worker_activity_excel',
                'parameters': ['month', 'year'],
            },
            {
                'name': 'Перемещение техники',
                'description': 'Отчет по перемещению техники между бригадами, с возможностью фильтрации.',
                'url': '{% url "dashboard:vehicle_movement_list" %}',  # Предполагаемый URL для списка перемещений
                'export_url': '{% url "dashboard:vehicle_movement_export_excel" %}',  # URL для экспорта
                'requires_selection': True,  # Требует фильтрации
                'selection_url_name': 'dashboard:vehicle_movement_export_excel',  # URL, где происходит фильтрация
                'parameters': ['month', 'year', 'brigade_from', 'brigade_to', 'driver', 'vehicle', 'start_date',
                               'end_date'],  # Список возможных фильтров
            },
        ]

        # Добавляем текущий месяц и год для удобства
        context['current_month'] = datetime.now().month
        context['current_year'] = datetime.now().year

        return context


class ReportSummaryView(ListView):
    ...


class ReportByBrigadeView(ListView):
    ...


class ReportListView(ListView):
    pass