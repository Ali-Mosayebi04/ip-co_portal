"""Email-sending logic for the ``meetings`` app.

Kept out of ``models.py`` and ``admin.py`` on purpose: sending email is
an I/O side effect, not persistence, so it belongs in its own module
that both the admin and (if needed later) a management command or API
view can call the same way.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Meeting, MeetingInvitation

INVITATION_SUBJECT_TEMPLATE = 'دعوت به جلسه: {title}'
CANCELLATION_SUBJECT_TEMPLATE = 'لغو جلسه: {title}'


@dataclass
class EmailBatchResult:
    sent: int = 0
    failed: int = 0
    skipped: int = 0

    @property
    def total(self) -> int:
        return self.sent + self.failed + self.skipped


def send_meeting_invitations(
    meeting: Meeting, *, only_new: bool = True
) -> EmailBatchResult:
    """Send the invitation email to a meeting's attendees.

    By default (``only_new=True``) this only emails attendees who
    haven't received one yet, so re-saving a meeting in the admin never
    spams everyone again — only newly-added attendees get an email.
    Pass ``only_new=False`` to force a resend to everyone (used by the
    explicit "resend invitations" admin action).

    Attendees without an email on file are skipped (and counted) rather
    than raising, since a missing email shouldn't block the rest of the
    batch from going out.
    """
    invitations = meeting.invitations.select_related("employee").all()
    if only_new:
        invitations = invitations.filter(sent_at__isnull=True)

    result = EmailBatchResult()
    pending = []
    for invitation in invitations:
        if not invitation.employee.email:
            result.skipped += 1
            continue
        pending.append(invitation)

    if not pending:
        return result

    connection = get_connection()
    connection.open()
    try:
        for invitation in pending:
            employee = invitation.employee
            body = render_to_string(
                "emails/meeting_invitation.txt",
                {"meeting": meeting, "employee": employee},
            )
            message = EmailMessage(
                subject=INVITATION_SUBJECT_TEMPLATE.format(title=meeting.title),
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[employee.email],
                connection=connection,
            )
            try:
                message.send(fail_silently=False)
            except Exception as exc:  # noqa: BLE001 — record it, keep going
                invitation.send_error = str(exc)[:500]
                invitation.save(update_fields=["send_error"])
                result.failed += 1
            else:
                invitation.sent_at = timezone.now()
                invitation.send_error = ""
                invitation.save(update_fields=["sent_at", "send_error"])
                result.sent += 1
    finally:
        connection.close()

    return result


def send_meeting_cancellations(meeting: Meeting) -> EmailBatchResult:
    """Notify everyone who was actually sent an invitation that the
    meeting has been cancelled. Attendees who never got the original
    invite (e.g. missing email) have nothing to be notified about."""
    invitations = (
        meeting.invitations.select_related("employee")
        .filter(sent_at__isnull=False, cancellation_sent_at__isnull=True)
    )

    result = EmailBatchResult()
    pending = list(invitations)
    if not pending:
        return result

    connection = get_connection()
    connection.open()
    try:
        for invitation in pending:
            employee = invitation.employee
            body = render_to_string(
                "emails/meeting_cancellation.txt",
                {"meeting": meeting, "employee": employee},
            )
            message = EmailMessage(
                subject=CANCELLATION_SUBJECT_TEMPLATE.format(title=meeting.title),
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[employee.email],
                connection=connection,
            )
            try:
                message.send(fail_silently=False)
            except Exception as exc:  # noqa: BLE001
                invitation.send_error = str(exc)[:500]
                invitation.save(update_fields=["send_error"])
                result.failed += 1
            else:
                invitation.cancellation_sent_at = timezone.now()
                invitation.save(update_fields=["cancellation_sent_at"])
                result.sent += 1
    finally:
        connection.close()

    return result
