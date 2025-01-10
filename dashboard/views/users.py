from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.forms import UserCreateForm
from dashboard.models import UserActionLog


class UserListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'dashboard/users/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_types'] = ContentType.objects.all()
        context['users'] = User.objects.all()
        context['logs'] = UserActionLog.objects.all().order_by('-action_time')[:10]
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'dashboard/users/user_detail.html'


class UserCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/users/user_form.html'
    success_url = '/dashboard/users'
    success_message = 'Пользователь успешно создан!'


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/users/user_form.html'
    success_message = 'Данные пользователя успешно обновлены'
    success_url = '/dashboard/users'


def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Пользователь успешно удалён!')
    return redirect('user_list')


class UserActionLogView(ListView):
    model = UserActionLog
    template_name = 'dashboard/users/user_action_log.html'
    context_object_name = 'logs'
    ordering = ['-action_time']
    paginate_by = 10
