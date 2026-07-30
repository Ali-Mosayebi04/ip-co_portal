"""Forms for creating and editing meetings with employee selection."""

from django import forms
from django.core.exceptions import ValidationError

from apps.workgroups.models import Employee

from .models import Meeting, MeetingRoom


class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings with attendee selection."""

    attendees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.select_related("workgroup").all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="شرکت‌کنندگان",
        help_text="کارمندانی که باید در جلسه حضور داشته باشند را انتخاب کنید.",
    )

    class Meta:
        model = Meeting
        fields = [
            "title",
            "agenda",
            "room",
            "date",
            "start_time",
            "end_time",
            "attendees",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان جلسه"}
            ),
            "agenda": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "دستور جلسه را وارد کنید...",
                }
            ),
            "room": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "start_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"},
                format="%H:%M",
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"},
                format="%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = MeetingRoom.objects.filter(is_active=True)
        self.fields["room"].empty_label = "اتاق را انتخاب کنید"

        if self.instance and self.instance.pk:
            self.fields["attendees"].initial = self.instance.attendees.all()

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        room = cleaned_data.get("room")
        date = cleaned_data.get("date")

        if start_time and end_time and start_time >= end_time:
            raise ValidationError(
                {"end_time": "ساعت پایان باید بعد از ساعت شروع باشد."}
            )

        if room and date and start_time and end_time:
            overlapping = (
                Meeting.objects.filter(
                    room=room,
                    date=date,
                    is_cancelled=False,
                )
                .exclude(pk=self.instance.pk if self.instance else None)
                .filter(
                    start_time__lt=end_time,
                    end_time__gt=start_time,
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

        return cleaned_data

    def save(self, commit=True):
        meeting = super().save(commit=commit)
        if commit:
            meeting.attendees.set(self.cleaned_data["attendees"])
        return meeting
