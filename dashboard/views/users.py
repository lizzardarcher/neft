from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from dashboard.forms import UserCreateForm, UserUpdateForm, GroupForm
from dashboard.models import UserActionLog


class UserListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'dashboard/users/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_types'] = ContentType.objects.all()
        context['users'] = User.objects.all().order_by('username')
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

class UserAccountUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class GroupListView(ListView):
    model = Group
    template_name = 'dashboard/users/group_list.html'
    context_object_name = 'groups'


class GroupCreateView(CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'dashboard/users/group_form.html'
    success_url = reverse_lazy('group_list')


class GroupUpdateView(UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'dashboard/users/group_form.html'
    success_url = reverse_lazy('group_list')

class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'dashboard/users/group_confirm_delete.html'
    success_url = reverse_lazy('group_list')