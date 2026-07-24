"""Template context processors for ``apps.home``.

Registered in ``config.settings.TEMPLATES``. This makes the header and
footer partials work the same way on *every* page — home, news,
work-group listings, etc. — without each view having to remember to
pass ``site_info``/``nav_items``/``quick_links`` into its context.
"""

from __future__ import annotations

from urllib.parse import quote

from django.http import HttpRequest
from django.urls import reverse
from django.utils import formats, timezone

from apps.meetings.models import Meeting
from apps.news.models import News
from apps.training.models import Course
from apps.workgroups.models import Employee

from .models import Announcement, NavItem, QuickLink, SiteInfo

_HEADER_NOTIFICATION_LIMIT = 6


def _build_header_notifications(request: HttpRequest, employee: Employee | None) -> list[dict]:
    notifications: list[dict] = []

    if employee is not None:
        meetings = (
            Meeting.objects.filter(
                invitations__employee=employee,
                is_cancelled=False,
                date__gte=timezone.localdate(),
            )
            .select_related('room')
            .order_by('date', 'start_time')
            .distinct()[:2]
        )
        for meeting in meetings:
            notifications.append(
                {
                    'kind': 'meeting',
                    'label': 'جلسه',
                    'title': meeting.title,
                    'meta': f"{formats.date_format(meeting.date, 'j F Y')} · {meeting.start_time.strftime('%H:%M')} · {meeting.room.name}",
                    'url': reverse('meetings:upcoming'),
                }
            )
    elif not request.user.is_authenticated:
        notifications.append(
            {
                'kind': 'account',
                'label': 'حساب کاربری',
                'title': 'برای مشاهده جلسات اختصاصی وارد شوید',
                'meta': 'ورود به پورتال داخلی ایپکو',
                'url': f"{reverse('login')}?next={quote(reverse('meetings:upcoming'))}",
            }
        )

    latest_news = News.objects.published().only('title', 'slug', 'published_at')[:2]
    for item in latest_news:
        notifications.append(
            {
                'kind': 'news',
                'label': 'خبر',
                'title': item.title,
                'meta': formats.date_format(item.published_at, 'j F Y'),
                'url': item.get_absolute_url(),
            }
        )

    latest_courses = Course.objects.published().only('title', 'slug', 'duration_hours', 'published_at')[:2]
    for item in latest_courses:
        duration_text = f"{item.duration_hours} ساعت" if item.duration_hours else 'دوره آموزشی'
        notifications.append(
            {
                'kind': 'training',
                'label': 'آموزش',
                'title': item.title,
                'meta': duration_text,
                'url': item.get_absolute_url(),
            }
        )

    latest_announcements = Announcement.objects.filter(is_active=True).only('title')[:1]
    for item in latest_announcements:
        notifications.append(
            {
                'kind': 'announcement',
                'label': 'اطلاعیه',
                'title': item.title,
                'meta': 'مشاهده در صفحه اصلی پورتال',
                'url': f"{reverse('home:index')}#announcements",
            }
        )

    return notifications[:_HEADER_NOTIFICATION_LIMIT]


def site_globals(request: HttpRequest) -> dict:
    employee = None
    if request.user.is_authenticated:
        employee = (
            Employee.objects.filter(user=request.user)
            .select_related('workgroup')
            .only('id', 'full_name', 'position', 'workgroup__name')
            .first()
        )

    header_notifications = _build_header_notifications(request, employee)

    return {
        'site_info': SiteInfo.load(),
        'nav_items': NavItem.objects.filter(is_active=True),
        'quick_links': QuickLink.objects.filter(is_active=True),
        'header_employee': employee,
        'header_notifications': header_notifications,
        'header_notification_count': len(header_notifications),
    }
