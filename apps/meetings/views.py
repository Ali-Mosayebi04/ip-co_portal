"""Views for the ``meetings`` app.

Provides both employee-facing views (see their own upcoming meetings) and
admin-only views (create, edit, delete meetings).
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from apps.workgroups.models import Employee

from .emails import send_meeting_cancellations, send_meeting_invitations
from .forms import MeetingForm
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


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to admin users only."""

    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(
            self.request,
            "شما اجازه دسترسی به این بخش را ندارید. فقط مدیران سیستم می‌توانند جلسات را مدیریت کنند."
        )
        return redirect('meetings:upcoming')


class MeetingListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all meetings for admins to manage."""

    model = Meeting
    template_name = "meetings/meeting_list.html"
    context_object_name = "meetings"
    paginate_by = 20

    def get_queryset(self):
        return (
            Meeting.objects.select_related("room", "organizer")
            .prefetch_related("attendees")
            .order_by("-date", "-start_time")
        )


class MeetingDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Detailed view of a single meeting for admins."""

    model = Meeting
    template_name = "meetings/meeting_detail.html"
    context_object_name = "meeting"

    def get_queryset(self):
        return Meeting.objects.select_related("room", "organizer").prefetch_related(
            "attendees__workgroup", "invitations__employee"
        )


class MeetingCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new meeting and send email invitations (admin only)."""

    model = Meeting
    form_class = MeetingForm
    template_name = "meetings/meeting_form.html"

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)

        result = send_meeting_invitations(self.object, only_new=True)
        if result.sent:
            messages.success(
                self.request,
                f"جلسه با موفقیت ایجاد شد و دعوت‌نامه برای {result.sent} نفر ارسال شد.",
            )
        if result.failed:
            messages.warning(
                self.request,
                f"ارسال دعوت‌نامه برای {result.failed} نفر با خطا مواجه شد.",
            )
        if result.skipped:
            messages.info(
                self.request,
                f"{result.skipped} نفر ایمیل ثبت‌شده‌ای ندارند.",
            )

        return response

    def get_success_url(self):
        return reverse("meetings:detail", kwargs={"pk": self.object.pk})


class MeetingUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Edit an existing meeting and notify newly-added attendees (admin only)."""

    model = Meeting
    form_class = MeetingForm
    template_name = "meetings/meeting_form.html"

    def get_queryset(self):
        return Meeting.objects.filter(is_cancelled=False)

    def form_valid(self, form):
        response = super().form_valid(form)

        result = send_meeting_invitations(self.object, only_new=True)
        if result.sent:
            messages.success(
                self.request,
                f"جلسه بروزرسانی شد و دعوت‌نامه برای {result.sent} شرکت‌کننده جدید ارسال شد.",
            )
        else:
            messages.success(self.request, "جلسه با موفقیت بروزرسانی شد.")

        if result.failed:
            messages.warning(
                self.request,
                f"ارسال دعوت‌نامه برای {result.failed} نفر با خطا مواجه شد.",
            )

        return response

    def get_success_url(self):
        return reverse("meetings:detail", kwargs={"pk": self.object.pk})


class MeetingDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Cancel a meeting and notify all attendees (admin only)."""

    model = Meeting
    template_name = "meetings/meeting_confirm_delete.html"
    success_url = reverse_lazy("meetings:list")

    def get_queryset(self):
        return Meeting.objects.filter(is_cancelled=False)

    def form_valid(self, form):
        meeting = self.get_object()
        meeting.cancel()

        result = send_meeting_cancellations(meeting)
        messages.success(
            self.request,
            f"جلسه لغو شد و {result.sent} اطلاعیه لغو ارسال شد.",
        )

        return redirect(self.success_url)
