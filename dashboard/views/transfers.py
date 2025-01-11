from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from dashboard.models import Transfer


class TransferHistoryView(LoginRequiredMixin, ListView):
    """Отображение истории перемещений оборудования."""
    model = Transfer
    template_name = 'dashboard/transfers/transfer_history.html'
    context_object_name = 'transfers'
    paginate_by = 30


