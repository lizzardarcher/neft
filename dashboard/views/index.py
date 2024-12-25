from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView

from dashboard.models import Brigade, Category, Equipment


class DashboardView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['brigades'] = Brigade.objects.all()
        context['categories'] = Category.objects.all()
        context['equipment'] = Equipment.objects.all()
        return context
