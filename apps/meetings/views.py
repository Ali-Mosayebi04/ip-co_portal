"""Views for the ``meetings`` app.

Booking itself stays admin-only (see ``apps.meetings.admin``) — this
module only adds the employee-facing side: letting a logged-in
employee see the meetings they've been invited to.
"""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.utils import timezone
from django.views.generic import TemplateView

from apps.workgroups.models import Employee

from .models import Meeting


class UpcomingMeetingsView(LoginRequiredMixin, TemplateView):
    """Meetings the logged-in employee is invited to, from today
    onward. If the logged-in account isn't linked to an ``Employee``
    record, we say so plainly instead of showing a confusing empty
    list — the fix is an admin linking the account, not the employee
    doing anything differently.
    """

    template_name = "meetings/upcoming.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        employee = self._get_employee()
        context["employee"] = employee
        context["meetings"] = self._get_upcoming_meetings(employee)
        return context

    def _get_employee(self) -> Employee | None:
        return Employee.objects.filter(user=self.request.user).select_related(
            "workgroup"
        ).first()

    @staticmethod
    def _get_upcoming_meetings(employee: Employee | None) -> QuerySet[Meeting]:
        if employee is None:
            return Meeting.objects.none()
        return (
            Meeting.objects.filter(
                invitations__employee=employee,
                is_cancelled=False,
                date__gte=timezone.localdate(),
            )
            .select_related("room", "organizer")
            .order_by("date", "start_time")
            .distinct()
        )
