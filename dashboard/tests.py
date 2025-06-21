import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neft.settings')
django.setup()
import time
from datetime import datetime
from datetime import date as dt
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
from django.test import TestCase

from dashboard.forms import WorkerActivityForm
from dashboard.models import WorkerActivity
from dashboard.utils.utils import get_days_in_month


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


def test_case_get_data_1(count):
    context = {}
    start_time_total = time.time()
    context['month'] = datetime.now().strftime('%m')
    context['year'] = datetime.now().strftime('%Y')
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

    employee_data = [
        {
            'user': user,
            'total_wa': WorkerActivity.objects.filter(user=user, date__month=context['month'],
                                                      date__year=context['year']).count(),
            'wa': [
                {'day': day,
                 'wa': WorkerActivity.objects.filter(user=user, date=get_date_from_year_month_day(context['year'],
                                                                                                  context[
                                                                                                      'month'],
                                                                                                  day)).last()}
                for day in context['days']
            ],
        } for user in context['users']
    ]

    context['employee_data'] = employee_data
    context['form'] = WorkerActivityForm
    end_time_total = time.time()
    print(f"({count}) Time total: {end_time_total - start_time_total}")
    return end_time_total - start_time_total


def test_case_get_data_2(count):
    context = {}
    start_time_total = time.time()
    context['month'] = datetime.now().strftime('%m')
    context['year'] = datetime.now().strftime('%Y')
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

    employee_data = [
        {
            'user': user,
            'total_wa': WorkerActivity.objects.filter(user=user, date__range=[
                get_date_from_year_month(context['year'], context['month']),
                get_date_from_year_month(context['next_year'], context['next_month'])]).count(),
            'wa': [
                {'day': day,
                 'wa': WorkerActivity.objects.filter(user=user, date=get_date_from_year_month_day(context['year'],
                                                                                                  context[
                                                                                                      'month'],
                                                                                                  day)).last()}
                for day in context['days']
            ],
        } for user in context['users']
    ]

    context['employee_data'] = employee_data
    context['form'] = WorkerActivityForm
    end_time_total = time.time()
    print(f"({count}) Time total: {end_time_total - start_time_total}")
    return end_time_total - start_time_total


def test_case_get_data_3(count):
    context = {}
    start_time_total = time.time()
    context['month'] = datetime.now().strftime('%m')
    context['year'] = datetime.now().strftime('%Y')
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

    print(f"Количество WorkerActivity: {all_worker_activities.count()}")  # Добавляем эту строку
    if all_worker_activities.count() == 0:
        print("Внимание: all_worker_activities пуст!")

    # 2. Преобразуем QuerySet в DataFrame.
    df = pd.DataFrame.from_records(all_worker_activities.values())

    # 3. Преобразуем столбец 'date' в datetime, если это еще не сделано.
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

    print(f"Размер DataFrame: {len(df)}")  # Добавляем эту строку
    print(f"Типы данных в DataFrame:\n{df.dtypes}")  # Добавляем эту строку

    if df.empty:
        print("Внимание: DataFrame пуст!")
        return  # Преждевременный выход, чтобы избежать ошибок



    employee_data = []
    for user in context['users']:
        user_id = user.id
        user_activities = df[df['user_id'] == user_id]
        print(f"{user_activities}")

        print(f"Размер user_activities для пользователя {user.username}: {len(user_activities)}")

        total_wa = len(user_activities)

        wa = []
        for day in context['days']:
            day_date = get_date_from_year_month_day(context['year'], context['month'], day)
            day_activity = user_activities[user_activities['date'] == pd.to_datetime(day_date)]

            if not day_activity.empty:
                # Получаем последнюю запись за день.
                wa_record = day_activity.iloc[-1].to_dict()  # Получаем последнюю запись за день
                wa.append({'day': day, 'wa': wa_record})
            else:
                wa.append({'day': day, 'wa': None})

        employee_data.append({
            'user': user,
            'total_wa': total_wa,
            'wa': wa
        })
    print(f"{employee_data}")
    context['employee_data'] = employee_data
    context['form'] = WorkerActivityForm
    end_time_total = time.time()
    print(f"({count}) Time total: {end_time_total - start_time_total}")
    return end_time_total - start_time_total


end_time_test_case_1 = 0
end_time_test_case_2 = 0
end_time_test_case_3 = 0

steps = 1
for i in range(steps):
    #
    # a = test_case_get_data_1(i)
    # end_time_test_case_1 += float(a)
    #
    # b = test_case_get_data_2(i)
    # end_time_test_case_2 += float(b)

    c = test_case_get_data_3(i)
    end_time_test_case_3 += float(c)

# print(f"Time test case 1: {end_time_test_case_1 / steps}")
# print(f"Time test case 2: {end_time_test_case_2 / steps}")
print(f"Time test case 2: {end_time_test_case_3 / steps}")
