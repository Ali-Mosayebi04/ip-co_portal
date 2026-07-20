from django.views.generic import DetailView, ListView

from .models import WorkGroup


class WorkGroupListView(ListView):
    model = WorkGroup
    template_name = "workgroups/list.html"
    context_object_name = "workgroups"


class WorkGroupDetailView(DetailView):
    model = WorkGroup
    template_name = "workgroups/detail.html"
    context_object_name = "workgroup"
