import jdatetime
from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='jalali')
def jalali(value, format_string='%d %B %Y'):
    """
    Convert datetime to Jalali (Persian) calendar format.

    Usage in templates:
        {{ date_value|jalali }}
        {{ date_value|jalali:"%d %B %Y - %H:%M" }}

    Common format codes:
        %Y - سال چهار رقمی (1403)
        %y - سال دو رقمی (03)
        %m - ماه دو رقمی (01-12)
        %B - نام کامل ماه (فروردین)
        %b - نام کوتاه ماه (فرو)
        %d - روز ماه دو رقمی (01-31)
        %j - روز سال (001-366)
        %A - نام کامل روز هفته (شنبه)
        %a - نام کوتاه روز هفته (ش)
        %H - ساعت 24 ساعته (00-23)
        %I - ساعت 12 ساعته (01-12)
        %M - دقیقه (00-59)
        %S - ثانیه (00-59)
        %p - قبل/بعد از ظهر
    """


    if not value:
        return ""

    # Make sure the datetime is timezone-aware
    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    # Convert to local timezone
    value = timezone.localtime(value)

    # Convert to Jalali date
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)

    # Format the date
    return jalali_date.strftime(format_string)


@register.filter(name='jalali_day')
def jalali_day(value):
    """Return just the day number in Jalali calendar."""
    if not value:
        return ""

    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    value = timezone.localtime(value)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.day


@register.filter(name='jalali_month')
def jalali_month(value):
    """Return the month name in Jalali calendar."""
    if not value:
        return ""

    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    value = timezone.localtime(value)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.strftime('%B')


@register.filter(name='jalali_year')
def jalali_year(value):
    """Return the year in Jalali calendar."""
    if not value:
        return ""

    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    value = timezone.localtime(value)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.year


@register.filter(name='jalali_weekday')
def jalali_weekday(value):
    """Return the weekday name in Jalali calendar."""
    if not value:
        return ""

    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    value = timezone.localtime(value)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.strftime('%A')


@register.simple_tag
def jalali_now(format_string='%d %B %Y'):
    """
    Display current date/time in Jalali calendar format.

    Usage in templates:
        {% jalali_now %}
        {% jalali_now "%A، %d %B %Y" %}
        {% jalali_now "%Y" %}
    """
    now = timezone.now()
    now = timezone.localtime(now)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=now)
    return jalali_date.strftime(format_string)
