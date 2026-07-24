import datetime

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.workgroups.models import Employee, WorkGroup

from .emails import send_meeting_cancellations, send_meeting_invitations
from .models import Meeting, MeetingInvitation, MeetingRoom

User = get_user_model()


class MeetingValidationTests(TestCase):
    def setUp(self):
        self.room = MeetingRoom.objects.create(name="اتاق کنفرانس ۱")
        self.tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    def _make_meeting(self, **overrides):
        defaults = dict(
            room=self.room,
            title="جلسه هماهنگی",
            date=self.tomorrow,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        defaults.update(overrides)
        return Meeting(**defaults)

    def test_end_time_before_start_time_is_rejected(self):
        meeting = self._make_meeting(
            start_time=datetime.time(11, 0), end_time=datetime.time(10, 0)
        )
        with self.assertRaises(ValidationError):
            meeting.full_clean()

    def test_valid_meeting_passes_clean(self):
        meeting = self._make_meeting()
        meeting.full_clean()  # should not raise

    def test_overlapping_booking_in_same_room_is_rejected(self):
        Meeting.objects.create(
            room=self.room,
            title="جلسه اول",
            date=self.tomorrow,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        conflicting = self._make_meeting(
            title="جلسه دوم",
            start_time=datetime.time(10, 30),
            end_time=datetime.time(11, 30),
        )
        with self.assertRaises(ValidationError):
            conflicting.full_clean()

    def test_back_to_back_bookings_do_not_conflict(self):
        Meeting.objects.create(
            room=self.room,
            title="جلسه اول",
            date=self.tomorrow,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        back_to_back = self._make_meeting(
            title="جلسه دوم", start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)
        )
        back_to_back.full_clean()  # should not raise

    def test_cancelled_meeting_does_not_block_the_room(self):
        existing = Meeting.objects.create(
            room=self.room,
            title="جلسه لغوشده",
            date=self.tomorrow,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        existing.cancel()
        new_meeting = self._make_meeting(title="جلسه جدید")
        new_meeting.full_clean()  # should not raise

    def test_different_rooms_do_not_conflict(self):
        other_room = MeetingRoom.objects.create(name="اتاق کنفرانس ۲")
        Meeting.objects.create(
            room=self.room,
            title="جلسه اول",
            date=self.tomorrow,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        meeting_elsewhere = self._make_meeting(room=other_room, title="جلسه دوم")
        meeting_elsewhere.full_clean()  # should not raise


class MeetingInvitationEmailTests(TestCase):
    def setUp(self):
        self.room = MeetingRoom.objects.create(name="اتاق کنفرانس ۱")
        self.group = WorkGroup.objects.create(name="فناوری اطلاعات")
        self.alice = Employee.objects.create(
            workgroup=self.group, full_name="علی رضایی", email="alice@example.com"
        )
        self.bob = Employee.objects.create(
            workgroup=self.group, full_name="بهروز احمدی", email="bob@example.com"
        )
        self.no_email = Employee.objects.create(
            workgroup=self.group, full_name="بدون ایمیل", email=""
        )
        self.meeting = Meeting.objects.create(
            room=self.room,
            title="جلسه هماهنگی هفتگی",
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        MeetingInvitation.objects.create(meeting=self.meeting, employee=self.alice)
        MeetingInvitation.objects.create(meeting=self.meeting, employee=self.bob)
        MeetingInvitation.objects.create(meeting=self.meeting, employee=self.no_email)

    def test_sends_one_email_per_attendee_with_an_address(self):
        result = send_meeting_invitations(self.meeting)
        self.assertEqual(result.sent, 2)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(len(mail.outbox), 2)
        recipients = {msg.to[0] for msg in mail.outbox}
        self.assertEqual(recipients, {"alice@example.com", "bob@example.com"})

    def test_email_mentions_room_and_time(self):
        send_meeting_invitations(self.meeting)
        body = mail.outbox[0].body
        self.assertIn("اتاق کنفرانس ۱", body)
        self.assertIn("10:00", body)

    def test_marks_invitations_as_sent(self):
        send_meeting_invitations(self.meeting)
        invitation = MeetingInvitation.objects.get(employee=self.alice)
        self.assertIsNotNone(invitation.sent_at)

    def test_resending_with_only_new_skips_already_sent(self):
        send_meeting_invitations(self.meeting)
        mail.outbox.clear()

        third = Employee.objects.create(
            workgroup=self.group, full_name="کارمند سوم", email="third@example.com"
        )
        MeetingInvitation.objects.create(meeting=self.meeting, employee=third)

        result = send_meeting_invitations(self.meeting, only_new=True)
        self.assertEqual(result.sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["third@example.com"])

    def test_force_resend_emails_everyone_again(self):
        send_meeting_invitations(self.meeting)
        mail.outbox.clear()

        result = send_meeting_invitations(self.meeting, only_new=False)
        self.assertEqual(result.sent, 2)
        self.assertEqual(len(mail.outbox), 2)


class MeetingCancellationEmailTests(TestCase):
    def setUp(self):
        self.room = MeetingRoom.objects.create(name="اتاق کنفرانس ۱")
        self.group = WorkGroup.objects.create(name="فناوری اطلاعات")
        self.alice = Employee.objects.create(
            workgroup=self.group, full_name="علی رضایی", email="alice@example.com"
        )
        self.meeting = Meeting.objects.create(
            room=self.room,
            title="جلسه هماهنگی",
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        MeetingInvitation.objects.create(meeting=self.meeting, employee=self.alice)

    def test_cancellation_only_notifies_people_who_were_invited(self):
        # Never sent an invitation in the first place, so there's
        # nothing to notify them about when the meeting is cancelled.
        self.meeting.cancel()
        result = send_meeting_cancellations(self.meeting)
        self.assertEqual(result.sent, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_cancellation_notifies_previously_invited_attendees(self):
        send_meeting_invitations(self.meeting)
        mail.outbox.clear()

        self.meeting.cancel()
        result = send_meeting_cancellations(self.meeting)

        self.assertEqual(result.sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("لغو", mail.outbox[0].subject)

    def test_cancel_sets_flags(self):
        self.meeting.cancel()
        self.meeting.refresh_from_db()
        self.assertTrue(self.meeting.is_cancelled)
        self.assertIsNotNone(self.meeting.cancelled_at)


class UpcomingMeetingsViewTests(TestCase):
    def setUp(self):
        self.room = MeetingRoom.objects.create(name="اتاق کنفرانس ۱")
        self.group = WorkGroup.objects.create(name="فناوری اطلاعات")

        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.employee = Employee.objects.create(
            workgroup=self.group,
            full_name="علی رضایی",
            email="alice@example.com",
            user=self.user,
        )

        self.other_user = User.objects.create_user(username="bob", password="pass12345")
        self.other_employee = Employee.objects.create(
            workgroup=self.group, full_name="بهروز احمدی", email="bob@example.com"
        )

        self.upcoming_meeting = Meeting.objects.create(
            room=self.room,
            title="جلسه هفتگی تیم",
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        MeetingInvitation.objects.create(
            meeting=self.upcoming_meeting, employee=self.employee
        )

        self.past_meeting = Meeting.objects.create(
            room=self.room,
            title="جلسه گذشته",
            date=datetime.date.today() - datetime.timedelta(days=1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        MeetingInvitation.objects.create(
            meeting=self.past_meeting, employee=self.employee
        )

        self.other_persons_meeting = Meeting.objects.create(
            room=self.room,
            title="جلسه شخص دیگر",
            date=datetime.date.today() + datetime.timedelta(days=2),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        MeetingInvitation.objects.create(
            meeting=self.other_persons_meeting, employee=self.other_employee
        )

    def test_requires_login(self):
        response = self.client.get(reverse("meetings:upcoming"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_shows_only_this_employees_upcoming_meetings(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("meetings:upcoming"))
        self.assertContains(response, "جلسه هفتگی تیم")
        self.assertNotContains(response, "جلسه گذشته")
        self.assertNotContains(response, "جلسه شخص دیگر")

    def test_cancelled_meeting_is_excluded(self):
        self.upcoming_meeting.cancel()
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("meetings:upcoming"))
        self.assertNotContains(response, "جلسه هفتگی تیم")

    def test_account_without_linked_employee_sees_helpful_message(self):
        unlinked_user = User.objects.create_user(
            username="charlie", password="pass12345"
        )
        self.client.login(username="charlie", password="pass12345")
        response = self.client.get(reverse("meetings:upcoming"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["employee"])
        self.assertContains(response, "متصل نیست")


class LoginFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_successful_login_redirects_to_upcoming_meetings(self):
        response = self.client.post(
            reverse("login"),
            {"username": "alice", "password": "pass12345"},
        )
        self.assertRedirects(response, reverse("meetings:upcoming"))

    def test_logout_requires_post(self):
        self.client.login(username="alice", password="pass12345")
        # Django 5's LogoutView only accepts POST; GET must not log the
        # user out (this would be a CSRF/link-based-logout footgun).
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_via_post_redirects_home(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home:index"))
