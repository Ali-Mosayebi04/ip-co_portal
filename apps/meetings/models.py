from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.workgroups.models import Employee


class MeetingRoom(models.Model):

    name = models.CharField("نام اتاق", max_length=100, unique=True)
    location = models.CharField("محل استقرار", max_length=200, blank=True)
    capacity = models.PositiveIntegerField("ظرفیت (نفر)", null=True, blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "اتاق جلسه"
        verbose_name_plural = "اتاق‌های جلسه"

    def __str__(self) -> str:
        return self.name


class Meeting(models.Model):

    room = models.ForeignKey(
        MeetingRoom,
        on_delete=models.PROTECT,
        related_name="meetings",
        verbose_name="اتاق",
        help_text="اتاق‌های دارای جلسه را نمی‌توان حذف کرد؛ در عوض غیرفعال کنید.",
    )
    organizer = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_meetings",
        verbose_name="برگزارکننده",
    )

    title = models.CharField("عنوان جلسه", max_length=200)
    agenda = models.TextField("دستور جلسه", blank=True)

    date = models.DateField("تاریخ برگزاری")
    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField("ساعت پایان")

    attendees = models.ManyToManyField(
        Employee,
        through="MeetingInvitation",
        related_name="meetings",
        verbose_name="شرکت‌کنندگان",
        blank=True,
    )

    is_cancelled = models.BooleanField("لغو شده", default=False)
    cancelled_at = models.DateTimeField("زمان لغو", null=True, blank=True)

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        verbose_name = "جلسه"
        verbose_name_plural = "جلسات"
        indexes = [
            models.Index(fields=["room", "date"], name="meeting_room_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"

    def clean(self) -> None:
        super().clean()

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {"end_time": "ساعت پایان باید بعد از ساعت شروع باشد."}
            )

        if self.room_id and self.date and self.start_time and self.end_time:
            overlapping = (
                Meeting.objects.filter(
                    room_id=self.room_id,
                    date=self.date,
                    is_cancelled=False,
                )
                .exclude(pk=self.pk)
                .filter(
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time,
                )
            )
            if overlapping.exists():
                raise ValidationError(
                    {
                        "room": (
                            "این اتاق در این بازه‌ی زمانی قبلاً برای جلسه‌ی دیگری "
                            "رزرو شده است."
                        )
                    }
                )

    def cancel(self) -> None:
        
        self.is_cancelled = True
        self.cancelled_at = timezone.now()
        self.save(update_fields=["is_cancelled", "cancelled_at", "updated_at"])


class MeetingInvitation(models.Model):

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="جلسه",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="meeting_invitations",
        verbose_name="کارمند",
    )

    sent_at = models.DateTimeField("زمان ارسال دعوت‌نامه", null=True, blank=True)
    send_error = models.CharField(
        "خطای ارسال", max_length=500, blank=True
    )

    cancellation_sent_at = models.DateTimeField(
        "زمان ارسال اطلاعیه لغو", null=True, blank=True
    )

    class Meta:
        verbose_name = "دعوت‌نامه جلسه"
        verbose_name_plural = "دعوت‌نامه‌های جلسه"
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "employee"], name="unique_meeting_employee"
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee} \u2192 {self.meeting}"
