from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views import View
import csv
from openpyxl import Workbook
from dashboard.models import Brigade, Category, Equipment, UserActionLog, Transfer, Document


class DashboardView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['brigades'] = Brigade.objects.all()
        context['categories'] = Category.objects.all()
        context['equipment'] = Equipment.objects.all()
        context['users'] = User.objects.all()
        context['user_log'] = UserActionLog.objects.all()
        context['transfers'] = Transfer.objects.all()
        context['document'] = Document.objects.all()
        context['month'] = datetime.now().strftime('%m')
        context['year'] = datetime.now().strftime('%Y')
        return context


class InstructionView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/instruction.html'


class BaseExportView(View):
    """Базовый класс для выгрузки данных."""
    model = None
    filename = None
    header = None

    def get_queryset(self):
        return self.model.objects.all()

    def get_data(self):
        """Возвращает данные для выгрузки."""
        queryset = self.get_queryset()
        data = []
        for obj in queryset:
            row = []
            for attr in self.header:
                if hasattr(obj, attr):
                    val = getattr(obj, attr)
                    if callable(val):
                        val = val()
                    row.append(str(val))
                else:
                    row.append('-')
            data.append(row)
        return data


class BrigadeCSVExportView(BaseExportView):
    """Выгрузка данных бригады в CSV."""
    model = Brigade
    filename = 'brigades.csv'
    header = ['id', 'name', 'description', 'customer', 'notes']

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'

        writer = csv.writer(response)
        writer.writerow(self.header)
        writer.writerows(self.get_data())
        return response


class BrigadeExcelExportView(BaseExportView):
    """Выгрузка данных бригады в Excel."""
    model = Brigade
    filename = 'brigades.xlsx'
    header = ['id', 'name', 'description', 'customer', 'notes']

    def get(self, request):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(self.header)
        for row in self.get_data():
            sheet.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'
        workbook.save(response)
        return response


class EquipmentCSVExportView(BaseExportView):
    """Выгрузка данных оборудования в CSV."""
    model = Equipment
    filename = 'equipments.csv'
    header = ['id', 'serial', 'name', 'category', 'brigade', 'condition', 'date_release', 'date_exploitation', 'manufacturer', 'certificate_start', 'certificate_end']

    def get_data(self):
        queryset = self.get_queryset()
        data = []
        for obj in queryset:
            row = [
                obj.id,
                obj.serial,
                obj.name,
                obj.category.name,
                obj.brigade.name,
                obj.get_condition_display(),
                obj.date_release,
                obj.date_exploitation,
                obj.manufacturer,
                obj.certificate_start,
                obj.certificate_end
            ]
            data.append(row)
        return data

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'

        writer = csv.writer(response)
        writer.writerow(self.header)
        writer.writerows(self.get_data())
        return response

class EquipmentExcelExportView(BaseExportView):
    """Выгрузка данных оборудования в Excel."""
    model = Equipment
    filename = 'equipments.xlsx'
    header = ['id', 'serial', 'name', 'category', 'brigade', 'condition', 'date_release', 'date_exploitation', 'manufacturer', 'certificate_start', 'certificate_end']

    def get_data(self):
        queryset = self.get_queryset()
        data = []
        for obj in queryset:
            row = [
                obj.id,
                obj.serial,
                obj.name,
                obj.category.name,
                obj.brigade.name,
                obj.get_condition_display(),
                obj.date_release,
                obj.date_exploitation,
                obj.manufacturer,
                obj.certificate_start,
                obj.certificate_end
            ]
            data.append(row)
        return data

    def get(self, request):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(self.header)
        for row in self.get_data():
            sheet.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'
        workbook.save(response)
        return response
