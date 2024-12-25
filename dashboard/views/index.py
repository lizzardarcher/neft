from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        # context['sch'] = PostSchedule.objects.filter(user=self.request.user)
        return context