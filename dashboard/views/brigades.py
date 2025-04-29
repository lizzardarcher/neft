from datetime import date
import calendar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Q, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.utils.timezone import datetime

from dashboard.forms import BrigadeForm, BrigadeActivityForm, WorkObjectForm
from dashboard.mixins import StaffOnlyMixin
from dashboard.models import Brigade, Equipment, Manufacturer, WorkerActivity, BrigadeActivity, WorkObject, UserProfile
from dashboard.utils.utils import get_days_in_month
from django.db.models import Q, Count
from django.db.models import Value, IntegerField, Case

class BrigadeListView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, ListView):
    model = Brigade
    context_object_name = 'brigades'
    template_name = 'dashboard/brigades/brigade_list.html'
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


class BrigadeDetailView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, DetailView):
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


class BrigadeStaffView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, TemplateView):
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
        context['prev_year'] = prev_year
        context['next_year'] = next_year
        # context['users'] = User.objects.annotate(
        #     total_wa=Count('workeractivity',
        #                    filter=Q(workeractivity__date__year=,
        #                             workeractivity__date__month=context['month'],
        #                             workeractivity__brigade=brigade, ))).filter(profile__brigade=brigade,
        #                                                                         is_staff=True).order_by(
        #     'username')
        # employee_data = [
        #     {
        #         'user': user,
        #         'total_wa': WorkerActivity.objects.filter(user=user, date__month=context['month'],
        #                                                   date__year=context['year']).count(),
        #         'wa': [
        #             {'day': day, 'wa': WorkerActivity.objects.filter(user=user, date__month=context['month'],
        #                                                              date__year=context['year'], date__day=day).last()}
        #             for day in context['days']
        #         ],
        #     } for user in context['users']
        # ]
        # context['employee_data'] = employee_data

        # 1. Пользователи, которые сейчас числятся в бригаде
        current_brigade_users = User.objects.filter(
            profile__brigade=brigade,
            is_staff=True,
            workeractivity__date__year=context['year'],
            workeractivity__date__month=context['month'],
            workeractivity__brigade=brigade
        ).annotate(
            has_wa=Case(
                When(workeractivity__date__year=context['year'], workeractivity__date__month=context['month'],
                     workeractivity__brigade=brigade, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            total_wa=Count('workeractivity',
                           filter=Q(workeractivity__date__year=context['year'], workeractivity__date__month=context['month'],
                                    workeractivity__brigade=brigade))
        )

        # 2. Пользователи, которые когда-либо работали в бригаде (через WorkerActivity)
        past_brigade_users = User.objects.filter(
            is_staff=True,
            workeractivity__date__year=context['year'],
            workeractivity__date__month=context['month'],
            workeractivity__brigade=brigade
        ).annotate(
            has_wa=Case(
                When(workeractivity__date__year=context['year'], workeractivity__date__month=context['month'],
                     workeractivity__brigade=brigade, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            total_wa=Count('workeractivity',
                           filter=Q(workeractivity__date__year=context['year'], workeractivity__date__month=context['month'],
                                    workeractivity__brigade=brigade))
        )

        # Объединяем два queryset-а и убираем дубликаты
        all_brigade_users = current_brigade_users.union(past_brigade_users).order_by('-has_wa',
                                                                                     'username')  # Убираем distinct(), так как union уже делает это

        context['users'] = all_brigade_users
        context['brigade_users'] = current_brigade_users
        employee_data = [
            {
                'user': user,
                'total_wa': WorkerActivity.objects.filter(user=user, date__month=context['month'],
                                                          date__year=context['year'], brigade=brigade).count(),
                'wa': [
                    {'day': day, 'wa': WorkerActivity.objects.filter(user=user, date__month=context['month'],
                                                                     date__year=context['year'], date__day=day,
                                                                     brigade=brigade).last()}
                    for day in context['days']
                ],
            } for user in all_brigade_users
        ]
        context['employee_data'] = employee_data


        return context


class BrigadeWorkView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/brigade_work.html'

    def form_valid(self, form):
        form = BrigadeActivityForm(brigade_id=int(self.request.path.split('/')[-5]), data=self.request.POST)
        if form.is_valid():
            form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = BrigadeActivityForm()
        context['work_object_form'] = WorkObjectForm()
        brigade_id = int(self.request.path.split('/')[-5])
        year = int(self.kwargs.get('year', datetime.now().year))
        month = int(self.kwargs.get('month', datetime.now().month))

        brigade = get_object_or_404(Brigade, pk=brigade_id)
        context['brigade'] = brigade

        activities = BrigadeActivity.objects.filter(
            brigade=brigade,
            date__year=year,
            date__month=month
        )
        work_objects = []
        for i in activities:
            if i.work_object:
                work_objects.append(i.work_object)
        context['work_objects'] = work_objects
        # context['work_objects'] = WorkObject.objects.all().order_by('name')

        cal = calendar.monthcalendar(year, month)  # Returns a list of lists
        context['calendar'] = cal

        context['year'] = year
        context['month'] = month if month > 9 else '0' + str(month)
        context['month_name'] = calendar.month_name[month]

        brigade_data = [
            {
                'brigade': brigade,
                'total_ba': BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year).count(),
                'ba': [
                    {'day': day,
                     'ba': BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year,
                                                          date__day=day).last()}
                    for day in get_days_in_month(month, year)
                ],
            }
        ]
        context['brigade_data'] = brigade_data
        context['days'] = get_days_in_month(month, year)

        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        context['prev_month_url'] = f'/dashboard/brigade/{brigade_id}/work/{prev_month}/{prev_year}'
        context['next_month_url'] = f'/dashboard/brigade/{brigade_id}/work/{next_month}/{next_year}'

        activities_by_day = {}
        for activity in activities:
            day = activity.date.day
            if day not in activities_by_day:
                activities_by_day[day] = []
            activities_by_day[day].append(activity)

        context['activities_by_day'] = activities_by_day

        return context


class BrigadeTableTotalView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, TemplateView):
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
                'total_ba': BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year).count(),
                'ba': [
                    {'day': day,
                     'ba': BrigadeActivity.objects.filter(brigade=brigade, date__month=month, date__year=year,
                                                          date__day=day).last()}
                    for day in get_days_in_month(month, year)
                ],
            } for brigade in brigades
        ]
        context['brigade_data'] = brigade_data

        context['form'] = BrigadeActivityForm()
        context['work_object_form'] = WorkObjectForm()
        work_objects = []
        for i in BrigadeActivity.objects.filter(date__month=month, date__year=year):
            if i.work_object:
                work_objects.append(i.work_object)
        work_objects = set(work_objects)

        context['work_objects'] = work_objects
        # context['work_objects'] = WorkObject.objects.all().order_by('name')
        context['month'] = month
        context['year'] = year
        context['current_month'] = datetime.now().month
        context['current_year'] = datetime.now().year
        context['days'] = get_days_in_month(month, year)
        context['brigades'] = brigades
        context['days_in_month'] = calendar.monthrange(year, month)[1]
        context['previous_month_url'] = self.get_month_url(month, year, -1)
        context['next_month_url'] = self.get_month_url(month, year, 1)

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


class BrigadeIndexView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/brigades/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = datetime.now().strftime('%m')
        context['year'] = datetime.now().strftime('%Y')
        context['brigade'] = get_object_or_404(Brigade, pk=self.request.path.split('/')[-1])
        context['staff_count'] = User.objects.filter(profile__brigade=context['brigade']).count()
        context['equipment_count'] = Equipment.objects.filter(brigade=context['brigade']).count()
        return context


class BrigadeCreateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, CreateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_create.html'
    form_class = BrigadeForm
    success_url = '/dashboard/brigades'

    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно создана!"


class BrigadeUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_update.html'
    form_class = BrigadeForm
    success_url = '/dashboard/brigades'

    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно обновлена!"


class BrigadeUpdateFromTotalView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_update.html'
    form_class = BrigadeForm

    def get_success_url(self):
        return reverse('brigade_table_total')

    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно обновлена!"


class BrigadeUpdateFromWorkView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = Brigade
    context_object_name = 'brigade'
    template_name = 'dashboard/brigades/brigade_form_update.html'
    form_class = BrigadeForm

    def get_success_url(self):
        return reverse('brigade_work', args=[self.kwargs.get('pk'), self.kwargs.get('month'), self.kwargs.get('year')])

    def get_success_message(self, cleaned_data):
        return f"Бригада {cleaned_data['name']} Успешно обновлена!"


def brigade_delete(request, brigade_id):
    brigade = get_object_or_404(Brigade, id=brigade_id)
    brigade.delete()
    messages.success(request, 'Бригада успешно удалена!')
    return redirect('brigade_list')


# def brigade_activity_create(request, brigade_id):
#     form = BrigadeActivityForm(request.POST)
#     brigade = get_object_or_404(Brigade, id=brigade_id)
#     date = request.POST.get('date')
#     work_type = request.POST.get('work_type')
#     try:
#         work_object = get_object_or_404(WorkObject, id=request.POST.get('work_object'))
#     except:
#         work_object = None
#     if brigade and work_type and date:
#         brigade_activity = BrigadeActivity.objects.filter(
#             brigade=brigade,
#             date=date, ).first()
#         if brigade_activity:
#             brigade_activity.brigade = brigade
#             brigade_activity.date = date
#             brigade_activity.work_object = work_object
#             brigade_activity.work_type = work_type
#             brigade_activity.save()
#             messages.success(request, f'Активность успешно обновлена!')
#         else:
#             BrigadeActivity.objects.create(
#                 brigade=brigade,
#                 date=date,
#                 work_object=work_object,
#                 work_type=work_type,
#             )
#             messages.success(request, f'Активность успешно создана!')
#         return redirect(request.META.get('HTTP_REFERER'))
#     else:
#         if form.is_valid():
#             activity = form.save(commit=False)
#             activity.brigade = brigade
#             activity.save()
#             messages.success(request, 'Активность успешно создана!')
#         else:
#             messages.error(request, 'Произошла ошибка при создании активности!')
#         return redirect(request.META.get('HTTP_REFERER'))
def brigade_activity_create(request, brigade_id):
    form = BrigadeActivityForm(request.POST)
    brigade = get_object_or_404(Brigade, id=brigade_id)
    date = request.POST.get('date')
    work_type = request.POST.get('work_type')
    if work_type == '-':
        BrigadeActivity.objects.filter(brigade=brigade, date=date).delete()
        messages.success(request, 'Активность успешно удалена!')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        try:
            work_object = get_object_or_404(WorkObject, id=request.POST.get('work_object'))
        except:
            work_object = None

        if brigade and work_type and date:
            brigade_activity = BrigadeActivity.objects.filter(
                brigade=brigade,
                date=date, ).first()
            if brigade_activity:
                brigade_activity.brigade = brigade
                brigade_activity.date = date
                brigade_activity.work_object = work_object
                brigade_activity.work_type = work_type

                # Добавляем работников бригады к активности
                for worker in UserProfile.objects.filter(brigade=brigade):
                    brigade_activity.workers.add(worker.user)

                brigade_activity.save()
                messages.success(request, f'Активность успешно обновлена!')
            else:
                brigade_activity = BrigadeActivity.objects.create(
                    brigade=brigade,
                    date=date,
                    work_object=work_object,
                    work_type=work_type,
                )

                # Добавляем работников бригады к активности
                for worker in UserProfile.objects.filter(
                        brigade=brigade):  # Получаем всех пользователей, связанных с бригадой
                    brigade_activity.workers.add(worker.user)

                messages.success(request, f'Активность успешно создана!')
            return redirect(request.META.get('HTTP_REFERER') + f'#{brigade.id}')
        else:
            if form.is_valid():
                activity = form.save(commit=False)
                activity.brigade = brigade

                # Добавляем работников бригады к активности
                for worker in UserProfile.objects.filter(
                        brigade=brigade):  # Получаем всех пользователей, связанных с бригадой
                    activity.workers.add(worker.user)

                activity.save()
                messages.success(request, 'Активность успешно создана!')
            else:
                messages.error(request, 'Произошла ошибка при создании активности!')
            return redirect(request.META.get('HTTP_REFERER'))


def work_object_create(request):
    if request.method == 'POST':
        form = WorkObjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объект успешно создан!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Произошла ошибка при создании объекта!')
            return redirect(request.META.get('HTTP_REFERER'))


def work_object_delete(request, work_object_id):
    work_object = get_object_or_404(WorkObject, id=work_object_id)
    work_object.delete()
    messages.success(request, 'Объект успешно удален!')
    return redirect(request.META.get('HTTP_REFERER'))


class WorkObjectUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = WorkObject
    context_object_name = 'work_object'
    template_name = 'dashboard/brigades/work_object_edit.html'
    form_class = WorkObjectForm

    def get_success_url(self):
        return f'/dashboard/brigade/brigade_table_total/?month={datetime.now().month}&year={datetime.now().year}'

    def get_success_message(self, cleaned_data):
        return f"Объект {cleaned_data['name']} Успешно обновлен!"


def get_locations(request):
    query = request.GET.get('term', '')  # Получаем текст, введенный пользователем
    locations = WorkObject.objects.values_list('name', flat=True).distinct()  # Получаем уникальные месторождения
    locations = [loc for loc in locations if query.lower() in loc.lower()]  # Фильтрация для поиска

    data = list(locations)  # Преобразуем в список
    return JsonResponse(data, safe=False)


class WorkObjectListView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = WorkObject
    context_object_name = 'work_objects'
    template_name = 'dashboard/brigades/work_object_list.html'


class WorkObjectDetailView(LoginRequiredMixin, StaffOnlyMixin, DetailView):
    model = WorkObject
    context_object_name = 'work_object'
    template_name = 'dashboard/brigades/work_object_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = BrigadeActivity.objects.filter(work_object=self.object).order_by('date')
        return context
