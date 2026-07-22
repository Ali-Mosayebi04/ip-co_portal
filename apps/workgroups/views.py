from __future__ import annotations

from django.db.models import Prefetch, QuerySet
from django.views.generic import DetailView, ListView

from .models import Employee, WorkGroup


class WorkGroupListView(ListView):
    """All work groups, e.g. rendered on a dedicated archive page (the
    header dropdown uses ``apps.workgroups.context_processors`` instead,
    since it needs to appear on every page, not just this one)."""

    model = WorkGroup
    template_name = "workgroups/list.html"
    context_object_name = "workgroups"


class WorkGroupDetailView(DetailView):
    """A single work group and the employees who belong to it."""

    model = WorkGroup
    template_name = "workgroups/detail.html"
    context_object_name = "workgroup"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[WorkGroup]:
        # One query for the group, one for its employees (in the right
        # order) — instead of N+1 queries as the template loops through
        # ``workgroup.employees.all``.
        return WorkGroup.objects.prefetch_related(
            Prefetch(
                "employees",
                queryset=Employee.objects.order_by("order", "full_name"),
            )
        )
