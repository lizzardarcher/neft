from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView

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
