import time
from datetime import datetime
from datetime import date as dt
import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Exists, OuterRef, Prefetch, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

from dashboard.forms import UserCreateForm, UserUpdateForm, GroupForm, UserUpdateByBrigadeForm, WorkerActivityForm, \
    UserUpdateStaffForm, WorkerDocumentForm
from dashboard.mixins import StaffOnlyMixin
from dashboard.models import UserActionLog, WorkerActivity, Brigade, WorkerDocument
from dashboard.utils.utils import get_days_in_month


class UserListView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'dashboard/users/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_types'] = ContentType.objects.all()
        context['users'] = User.objects.filter(is_staff=True).order_by('username')
        context['logs'] = UserActionLog.objects.all().order_by('-action_time')[:10]
        return context


class UserDetailView(LoginRequiredMixin, StaffOnlyMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'dashboard/users/user_detail.html'


class UserCreateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/users/user_form.html'
    success_url = '/dashboard/users'
    success_message = 'Пользователь успешно создан!'


class UserUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/users/user_form.html'
    success_message = 'Данные пользователя успешно обновлены'
    success_url = '/dashboard/users'


class UserAccountUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'dashboard/users/user_account_form.html'
    success_message = 'Данные пользователя успешно обновлены'
    success_url = '/dashboard/users'

    def get_success_url(self):
        if 'users' in self.request.path:
            return self.success_url
        else:
            return f'/dashboard/user/{self.request.user.id}/detail'


class UserUpdateByBrigadeView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateByBrigadeForm
    template_name = 'dashboard/users/user_by_brigade_form.html'
    success_message = 'Данные пользователя успешно обновлены!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brigade_id'] = self.kwargs.get('brigade_id')
        return context

    def get_success_url(self):
        return reverse('brigade_staff', args=[self.kwargs.get('brigade_id')])


class UserStaffUpdateView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateStaffForm
    template_name = 'dashboard/users/user_staff_form.html'
    success_message = 'Данные пользователя успешно обновлены!'

    def get_success_url(self):
        return reverse('staff_table_total')


def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Пользователь успешно удалён!')
    return redirect('user_list')


class UserActionLogView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = UserActionLog
    template_name = 'dashboard/users/user_action_log.html'
    context_object_name = 'logs'
    ordering = ['-action_time']
    paginate_by = 10


class GroupListView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = Group
    template_name = 'dashboard/users/group_list.html'
    context_object_name = 'groups'


class GroupCreateView(LoginRequiredMixin, StaffOnlyMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'dashboard/users/group_form.html'
    success_url = reverse_lazy('group_list')


class GroupUpdateView(LoginRequiredMixin, StaffOnlyMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'dashboard/users/group_form.html'
    success_url = reverse_lazy('group_list')


class GroupDeleteView(LoginRequiredMixin, StaffOnlyMixin, DeleteView):
    model = Group
    template_name = 'dashboard/users/group_confirm_delete.html'
    success_url = reverse_lazy('group_list')


class WorkerActivityCreateView(LoginRequiredMixin, StaffOnlyMixin, CreateView):
    model = WorkerActivity
    form_class = WorkerActivityForm
    template_name = 'dashboard/users/worker_activity_form.html'

    def get_success_url(self):
        month = self.kwargs.get('month')  # Получаем месяц из kwargs
        year = self.kwargs.get('year')  # Получаем год из kwargs
        return reverse('brigade_staff', args=[self.kwargs.get('brigade_id'), month, year])


@csrf_exempt
def create_worker_activity(request):
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.GET.get('user_id').split('/')[0])
        brigade = get_object_or_404(Brigade, id=request.POST.get('brigade'))
        work_type = request.POST.get('work_type')
        date = request.POST.get('date')
        month = request.POST.get('month')
        year = request.POST.get('year')
        if work_type == '-':
            WorkerActivity.objects.filter(user=user, date=date).delete()
            messages.success(request, 'Активность успешно удалена!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            if brigade and user and work_type and date:
                # Обновление или создание активности

                worker_activity = WorkerActivity.objects.filter(user=user, date=date).first()

                if worker_activity:
                    worker_activity.work_type = work_type
                    worker_activity.brigade = brigade
                    worker_activity.save()
                else:
                    WorkerActivity.objects.create(
                        user=user,
                        brigade=brigade,
                        date=date,
                        work_type=work_type
                    )
                if not worker_activity:
                    messages.success(request, 'Активность успешно создана!')
                else:
                    messages.success(request, 'Активность успешно обновлена!')
                return redirect(request.META.get('HTTP_REFERER') + f'#{user.id}')
            else:
                messages.error(request, 'Произошла ошибка при создании активности!')
                return redirect('brigade_staff', pk=request.GET.get('brigade_id'))
    else:
        messages.error(request, 'Произошла ошибка при создании активности!')
        return redirect('brigade_staff', pk=request.GET.get('brigade_id'))


def get_date_from_year_month_day(year, month, day):
    try:
        year = int(year)
        month = int(month)
        day = int(day)

        return dt(year, month, day)
    except ValueError as e:
        ...


def get_date_from_year_month(year, month):
    try:
        year = int(year)
        month = int(month)

        return dt(year, month, 1)
    except ValueError as e:
        ...


class StaffTableTotalView(LoginRequiredMixin, StaffOnlyMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/users/staff_table_total.html'

    def get_context_data(self, **kwargs):
        start_time_1 = time.time()
        context = super().get_context_data(**kwargs)
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
        context['users'] = User.objects.annotate(
            has_wa=Exists(WorkerActivity.objects.filter(user=OuterRef('pk'),
                                                        date__month=context['month'],
                                                        date__year=context['year']))).filter(is_staff=True).order_by(
            '-has_wa', 'first_name')

        start_date = get_date_from_year_month(context['year'], context['month'])
        end_date = get_date_from_year_month(context['next_year'], context['next_month'])

        # 1. Получаем все WorkerActivity для всех пользователей и дат одним запросом.
        all_worker_activities = WorkerActivity.objects.filter(
            user__in=context['users'],
            date__range=[start_date, end_date]
        ).select_related('user')

        # 2. Преобразуем QuerySet в DataFrame.
        df = pd.DataFrame.from_records(all_worker_activities.values())

        # 3. Преобразуем столбец 'date' в datetime, если это еще не сделано.
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])

        employee_data = []

        if df.empty:
            context['users'] = User.objects.all().exclude(username__contains='1').order_by('first_name')
            for user in context['users']:
                user_activities = context['days']
                total_wa = len(user_activities)

                wa = []
                for day in context['days']:
                    wa.append({'day': day, 'wa': None})
                employee_data.append({
                    'user': user,
                    'total_wa': total_wa,
                    'wa': wa
                })
        else:
            for user in context['users']:
                user_id = user.id
                user_activities = df[df['user_id'] == user_id]

                total_wa = len(user_activities)

                wa = []
                for day in context['days']:
                    day_date = get_date_from_year_month_day(context['year'], context['month'], day)
                    day_activity = user_activities[user_activities['date'] == pd.to_datetime(day_date)]

                    if not day_activity.empty:
                        wa_record = day_activity.iloc[-1].to_dict()
                        wa.append({'day': day, 'wa': wa_record})
                    else:
                        wa.append({'day': day, 'wa': None})

                employee_data.append({
                    'user': user,
                    'total_wa': total_wa,
                    'wa': wa
                })

        context['employee_data'] = employee_data
        context['form'] = WorkerActivityForm
        end_time_1 = time.time()
        context['load_time_1'] = float(end_time_1 - start_time_1)
        return context


@login_required
def document_list(request):
    documents = WorkerDocument.objects.all()
    return render(request, 'dashboard/users/worker_document_list.html', {'documents': documents})


@login_required
def worker_document_create(request):
    if request.method == 'POST':
        form = WorkerDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('worker_document_list')
    else:
        form = WorkerDocumentForm()
    return render(request, 'dashboard/users/worker_document_create.html', {'form': form})


@login_required
def worker_document_delete(request, pk):
    document = get_object_or_404(WorkerDocument, pk=pk)
    document.delete()
    messages.success(request, 'Документ успешно удален!')
    return redirect('worker_document_list')
