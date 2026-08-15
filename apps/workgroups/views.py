from __future__ import annotations

from django.db.models import Prefetch, QuerySet
from django.views.generic import DetailView, ListView

from .models import Employee, WorkGroup


class WorkGroupListView(ListView):
   
    model = WorkGroup
    template_name = "workgroups/list.html"
    context_object_name = "workgroups"


class WorkGroupDetailView(DetailView):

    model = WorkGroup
    template_name = "workgroups/detail.html"
    context_object_name = "workgroup"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[WorkGroup]:
        return WorkGroup.objects.prefetch_related(
            Prefetch(
                "employees",
                queryset=Employee.objects.order_by("order", "full_name"),
            )
        )
