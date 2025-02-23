from datetime import date
import calendar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.utils.timezone import datetime
from dashboard.forms import BrigadeForm, BrigadeActivityForm
from dashboard.models import Brigade, Equipment, Manufacturer, WorkerActivity, BrigadeActivity
from dashboard.utils.utils import get_days_in_month


class BrigadeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Brigade
    context_object_name = 'brigades'
    template_name = 'dashboard/brigades/brigade_list.html'
    paginate_by = 30
    ordering = 'name'

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
                sort_by = f"-{sort_by}"
                equipments = equipments.order_by(sort_by)
            else:
                equipments = equipments.order_by(sort_by)

        # Добавляем пагинацию
        paginator = Paginator(equipments, 30)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = super().get_context_data(**kwargs)
        context['equipments'] = page_obj
        context['page_obj'] = page_obj
        context['now_date'] = date.today()
        context['manufacturers'] = Manufacturer.objects.all().order_by('name')
        return context

class BrigadeStaffView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/brigade_staff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brigade = get_object_or_404(Brigade, pk=self.request.path.split('/')[-2])
        context['brigade'] = brigade
        context['month'] = self.request.GET.get('month', datetime.now().strftime('%m'))
        context['year'] = self.request.GET.get('year', datetime.now().strftime('%Y'))
        context['days'] = get_days_in_month(int(context['month']), int(context['year']))
        context['date_m_y'] = datetime.now().strftime('%m-%Y')
        prev_month = int(context['month']) - 1
        next_month = int(context['month']) + 1
        prev_year = int(context['year'])
        next_year = int(context['year'])
        if prev_month < 1:
            prev_month = 12
            prev_year = int(context['year']) - 1
        if str(prev_month).__len__() == 1:
            prev_month = '0' + str(prev_month)
        if next_month > 12:
            next_month = 1
            next_year = int(context['year']) + 1
        if str(next_month).__len__() == 1:
            next_month = '0' + str(next_month)
        context['prev_month'] = str(prev_month)
        context['next_month'] = str(next_month)
        context['prev_year']  = prev_year
        context['next_year']  = next_year
        context['users'] = User.objects.annotate(
            total_wa=Count('workeractivity',
            filter=Q(workeractivity__date__year=context['year'],
                     workeractivity__date__month=context['month'],
                     workeractivity__brigade=brigade,))).filter(profile__brigade=brigade).order_by('username')
        employee_data = [
            {
                'user': user,
                'total_wa': WorkerActivity.objects.filter(user=user, date__month=context['month'], date__year=context['year'], brigade=context['brigade']).count(),
                'wa': [
                    {'day': day, 'wa': WorkerActivity.objects.filter(user=user, date__month=context['month'], date__year=context['year'], date__day=day).last()} for day in context['days']
                ],
            } for user in context['users']
        ]
        context['employee_data'] = employee_data
        return context

class BrigadeWorkView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/brigade_work.html'

    def form_valid(self, form):
        form = BrigadeActivityForm(brigade_id=int(self.request.path.split('/')[-5]), data=self.request.POST)
        if form.is_valid():
            form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = BrigadeActivityForm()

        brigade_id = int(self.request.path.split('/')[-5])
        year = int(self.kwargs.get('year', datetime.now().year))
        month = int(self.kwargs.get('month', datetime.now().month))

        brigade = get_object_or_404(Brigade, pk=brigade_id)
        context['brigade'] = brigade

        # Fetch activities for the selected month and brigade
        activities = BrigadeActivity.objects.filter(
            brigade=brigade,
            date__year=year,
            date__month=month
        )

        # Build the calendar structure (list of weeks, each a list of days)
        cal = calendar.monthcalendar(year, month)  # Returns a list of lists
        context['calendar'] = cal

        # Pass the current year and month for display
        context['year'] = year
        context['month'] = month if month > 9 else '0' + str(month)
        context['month_name'] = calendar.month_name[month]

        # Generate links for previous and next months
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        context['prev_month_url'] = f'/dashboard/brigade/{brigade_id}/work/{prev_month}/{prev_year}'
        context['next_month_url'] = f'/dashboard/brigade/{brigade_id}/work/{next_month}/{next_year}'

        #Prepare dictionary with all activies grouped by days
        activities_by_day = {}
        for activity in activities:
            day = activity.date.day
            if day not in activities_by_day:
                activities_by_day[day] = []
            activities_by_day[day].append(activity)

        context['activities_by_day'] = activities_by_day

        return context


class BrigadeTableTotalView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/brigade_work_total.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = int(self.request.GET.get('month', datetime.now().month))
        year = int(self.request.GET.get('year', datetime.now().year))
        brigades = Brigade.objects.all().order_by('name')

        if not 1 <= month <= 12:
            month = datetime.now().month
        if not 1900 <= year <= datetime.now().year + 10:
            year = datetime.now().year

        brigade_data = [
            {
                'brigade': brigade,
                'total_ba':  BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year).count(),
                'ba': [
                    {'day': day, 'ba': BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year, date__day=day).last()}
                    for day in get_days_in_month(month, year)
                ],
            } for brigade in brigades
        ]

        context['brigade_data'] = brigade_data
        context['month']= month
        context['year']= year
        context['current_month'] = datetime.now().month
        context['current_year'] = datetime.now().year
        context['days'] = get_days_in_month(month, year)
        context['brigades']= brigades
        context['days_in_month']= calendar.monthrange(year, month)[1]
        context['previous_month_url']= self.get_month_url(month, year, -1)
        context['next_month_url']= self.get_month_url(month, year, 1)

        return context

    def get_month_url(self, month, year, offset):
        new_month = month + offset
        new_year = year

        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1

        return reverse('brigade_table_total') + f'?month={new_month}&year={new_year}'

class BrigadeIndexView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = datetime.now().strftime('%m')
        context['year'] = datetime.now().strftime('%Y')
        context['brigade'] = get_object_or_404(Brigade, pk=self.request.path.split('/')[-1])
        context['staff_count'] = User.objects.filter(profile__brigade=context['brigade']).count()
        context['equipment_count'] = Equipment.objects.filter(brigade=context['brigade']).count()
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


def brigade_activity_create(request, brigade_id):
    brigade = get_object_or_404(Brigade, id=brigade_id)
    form = BrigadeActivityForm(request.POST)
    date = request.POST.get('date')
    work_type = request.POST.get('work_type')
    if brigade and work_type and date:
        brigade_activity, created = BrigadeActivity.objects.update_or_create(
            brigade=brigade,
            date=date,
            defaults={'work_type': work_type}
        )
        if created:
            messages.success(request, 'Активность успешно создана!')
        else:
            messages.success(request, 'Активность успешно обновлена!')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        if form.is_valid():
            activity = form.save(commit=False)
            activity.brigade = brigade
            activity.save()
            messages.success(request, 'Активность успешно создана!')
        else:
            messages.error(request, 'Произошла ошибка при создании активности!')
        return redirect(request.META.get('HTTP_REFERER'))