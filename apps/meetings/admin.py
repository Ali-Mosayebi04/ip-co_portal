from django.contrib import admin, messages

from .emails import send_meeting_cancellations, send_meeting_invitations
from .models import Meeting, MeetingInvitation, MeetingRoom


@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "location")


class MeetingInvitationInline(admin.TabularInline):
    """Add/remove attendees here. ``sent_at``/``send_error`` are
    read-only status columns — a delivery report, not something an
    admin edits by hand."""

    model = MeetingInvitation
    extra = 1
    autocomplete_fields = ("employee",)
    fields = ("employee", "sent_at", "send_error", "cancellation_sent_at")
    readonly_fields = ("sent_at", "send_error", "cancellation_sent_at")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "room",
        "date",
        "start_time",
        "end_time",
        "organizer",
        "attendee_count",
        "is_cancelled",
    )
    list_filter = ("room", "is_cancelled", "date")
    search_fields = ("title", "agenda")
    date_hierarchy = "date"
    autocomplete_fields = ("organizer",)
    readonly_fields = ("is_cancelled", "cancelled_at", "created_at", "updated_at")
    inlines = [MeetingInvitationInline]
    actions = ["resend_invitations", "cancel_meetings"]
    fieldsets = (
        (None, {"fields": ("title", "agenda", "room", "organizer")}),
        ("زمان‌بندی", {"fields": ("date", "start_time", "end_time")}),
        (
            "وضعیت",
            {"fields": ("is_cancelled", "cancelled_at", "created_at", "updated_at")},
        ),
    )

    @admin.display(description="تعداد شرکت‌کنندگان")
    def attendee_count(self, obj):
        return obj.invitations.count()

    def save_model(self, request, obj, form, change):
        if not change and not obj.organizer_id:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Runs after the inline MeetingInvitation rows have been saved,
        # so the attendee list on `form.instance` is final. Only
        # newly-added attendees (sent_at is still empty) get emailed —
        # editing an existing meeting never re-spams everyone.
        super().save_related(request, form, formsets, change)

        if form.instance.is_cancelled:
            return

        result = send_meeting_invitations(form.instance, only_new=True)
        if result.sent:
            messages.success(
                request,
                f"دعوت‌نامه برای {result.sent} نفر از شرکت‌کنندگان جدید ارسال شد.",
            )
        if result.failed:
            messages.warning(
                request,
                f"ارسال دعوت‌نامه برای {result.failed} نفر با خطا مواجه شد؛ "
                "جزئیات خطا را در ردیف مربوطه ببینید.",
            )
        if result.skipped:
            messages.warning(
                request,
                f"{result.skipped} نفر از شرکت‌کنندگان ایمیل ثبت‌شده‌ای ندارند "
                "و دعوت‌نامه‌ای برایشان ارسال نشد.",
            )

    @admin.action(description="ارسال دعوت‌نامه به شرکت‌کنندگان جدید")
    def resend_invitations(self, request, queryset):
        total_sent = total_failed = 0
        for meeting in queryset:
            result = send_meeting_invitations(meeting, only_new=True)
            total_sent += result.sent
            total_failed += result.failed
        self.message_user(
            request,
            f"مجموعاً {total_sent} دعوت‌نامه ارسال شد ({total_failed} خطا).",
            level=messages.SUCCESS if not total_failed else messages.WARNING,
        )

    @admin.action(description="لغو جلسه و اطلاع‌رسانی به شرکت‌کنندگان")
    def cancel_meetings(self, request, queryset):
        cancelled = 0
        total_notified = 0
        for meeting in queryset.filter(is_cancelled=False):
            meeting.cancel()
            result = send_meeting_cancellations(meeting)
            total_notified += result.sent
            cancelled += 1
        self.message_user(
            request,
            f"{cancelled} جلسه لغو شد و {total_notified} اطلاعیه لغو ارسال شد.",
            level=messages.SUCCESS,
        )
