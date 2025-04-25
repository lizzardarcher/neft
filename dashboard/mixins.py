from django.shortcuts import redirect


class StaffOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('worker_document_list')
        return super().dispatch(request, *args, **kwargs)