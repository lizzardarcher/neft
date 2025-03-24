import calendar
from datetime import datetime
from re import search

import openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views import View
import csv
from openpyxl import Workbook

from dashboard.models import Brigade, Category, Equipment, UserActionLog, Transfer, Document, BrigadeActivity, \
    WorkerActivity, WorkObject, VehicleMovement
from dashboard.utils.utils import get_days_in_month


class DashboardView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['brigades_count'] = Brigade.objects.all().count()
        context['categories_count'] = Category.objects.all().count()
        context['equipment_count'] = Equipment.objects.all().count()
        context['work_object_count'] = WorkObject.objects.all().count()
        context['users_count'] = User.objects.all().count()
        context['user_log_count'] = UserActionLog.objects.all().count()
        context['transfers_count'] = Transfer.objects.all().count()
        context['vehicle_movement_count'] = VehicleMovement.objects.all().count()
        context['document_count'] = Document.objects.all().count()
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

class EquipmentExcelExportView(LoginRequiredMixin, View):
    """Выгрузка данных оборудования в Excel."""
    filename = 'equipments.xlsx'
    header = ['id', 'serial', 'name', 'category', 'brigade', 'condition', 'date_release', 'date_exploitation', 'manufacturer', 'certificate_start', 'certificate_end']

    def get(self, request, *args, **kwargs):

        search_request = request.GET.get("search")
        if search_request:
            equipment_by_name = Equipment.objects.filter(name__icontains=search_request)
            equipment_by_serial = Equipment.objects.filter(serial__icontains=search_request)
            queryset = (equipment_by_name | equipment_by_serial)
        else:
            queryset = Equipment.objects.all()

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

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(self.header)
        for row in data:
            sheet.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'
        workbook.save(response)
        return response


class BrigadeActivityExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))

        if not 1 <= month <= 12:
            month = datetime.now().month
        if not 1900 <= year <= datetime.now().year + 10:
            year = datetime.now().year

        brigades = Brigade.objects.all().order_by('name')
        days_in_month = calendar.monthrange(year, month)[1]
        days = get_days_in_month(month, year)

        # Create a new workbook and add a worksheet.
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = f"Brigade Activities - {calendar.month_name[month]} {year}"

        # Add headers
        headers = ['Бригада'] + [f'{day}' for day in days] + ['Итого']
        worksheet.append(headers)

        # Define color mapping for work types
        color_mapping = {
            '(ЗБС) Бурение': 'FFFF0000',  # Red
            '(ЗБС) бурение горизонта': 'FF00FF00',  # Green
            '(ЗБС) шаблонирование + ГИС': 'FF0000FF',  # Blue
            '(ЗБС) спуск хвостовика': 'FFFFFF00',  # Yellow
            '(ВНС) бурение кондуктора': 'FF00FFFF',  # Cyan
            '(ВНС) бурение ЭК': 'FFFF00FF',  # Magenta
            '(ВНС) бурение горизонта': 'FFC0C0C0',  # Light Gray
            '(ВНС) спуск хвостовика': 'FF808080',  # Dark Gray
            'Переезд': 'FFA52A2A',  # Brown
            'Простой': 'FFFFC0CB',  # Pink
            'Авария': 'FF800000',  # Maroon
        }

        # Populate data
        for brigade in brigades:
            row_data = [brigade.name]
            total_ba = 0
            for day in days:
                ba = BrigadeActivity.objects.filter(brigade=brigade, date__day=day, date__month=month, date__year=year).last()
                try:
                    activity_str = ba.work_object.short_name
                except:
                    activity_str = ""
                row_data.append(activity_str)
                if ba:
                    total_ba += 1  # Increment the total count for the brigade

            row_data.append(total_ba)  # Add the total to the row
            worksheet.append(row_data)

        # Add formatting (optional)
        # Example: Bold the header row
        for cell in worksheet[1]:
            cell.font = openpyxl.styles.Font(bold=True)


        # Create the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=brigade_activities_{month}_{year}.xlsx'

        # Save the workbook to the response
        workbook.save(response)

        return response


class WorkerActivityExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))

        if not 1 <= month <= 12:
            month = datetime.now().month
        if not 1900 <= year <= datetime.now().year + 10:
            year = datetime.now().year

        brigades = Brigade.objects.all().order_by('name')
        days_in_month = calendar.monthrange(year, month)[1]
        days = get_days_in_month(month, year)

        users = User.objects.all().order_by('last_name', 'first_name')

        # Create a new workbook and add a worksheet.
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = f"Brigade Activities - {calendar.month_name[month]} {year}"

        # Add headers
        headers = ['ФИО'] + ['Должность'] + ['Бригада'] + [f'{day}' for day in days] + ['Итого']
        worksheet.append(headers)

        # Populate data
        for user in users:
            row_data = [user.get_full_name(), user.profile.position, user.profile.brigade.__str__()]
            total_ba = 0
            for day in days:
                wa = WorkerActivity.objects.filter(user=user, date__day=day, date__month=month, date__year=year).last()
                try:
                    activity_str = wa.work_type
                except:
                    activity_str = ""
                row_data.append(activity_str)
                if wa:
                    total_ba += 1  # Increment the total count for the brigade

            row_data.append(total_ba)  # Add the total to the row
            worksheet.append(row_data)

        # Add formatting (optional)
        # Example: Bold the header row
        for cell in worksheet[1]:
            cell.font = openpyxl.styles.Font(bold=True)

        # Create the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=brigade_activities_{month}_{year}.xlsx'

        # Save the workbook to the response
        workbook.save(response)

        return response