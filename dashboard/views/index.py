from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        # context['sch'] = PostSchedule.objects.filter(user=self.request.user)
        return context
