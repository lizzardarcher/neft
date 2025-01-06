from django.views.generic import ListView

from dashboard.models import UserActionLog


class ReportListView(ListView):
    ...

class ReportSummaryView(ListView):
    ...


class ReportByBrigadeView(ListView):
    ...

