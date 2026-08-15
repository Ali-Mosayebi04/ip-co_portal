import jdatetime
from django import template
from django.utils import timezone
import datetime

register = template.Library()


def _to_jalali(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        value = timezone.localtime(value)
        return jdatetime.datetime.fromgregorian(datetime=value)

    if isinstance(value, datetime.date):
        return jdatetime.date.fromgregorian(date=value)

    return None


@register.filter(name="jalali")
def jalali(value, format_string="%d %B %Y"):
    jalali_date = _to_jalali(value)
    if jalali_date is None:
        return ""

    return jalali_date.strftime(format_string)


@register.filter(name="jalali_day")
def jalali_day(value):
    jalali_date = _to_jalali(value)
    if jalali_date is None:
        return ""

    return jalali_date.day


@register.filter(name="jalali_month")
def jalali_month(value):
    jalali_date = _to_jalali(value)
    if jalali_date is None:
        return ""

    return jalali_date.strftime("%B")


@register.filter(name="jalali_year")
def jalali_year(value):
    jalali_date = _to_jalali(value)
    if jalali_date is None:
        return ""

    return jalali_date.year


@register.filter(name="jalali_weekday")
def jalali_weekday(value):
    jalali_date = _to_jalali(value)
    if jalali_date is None:
        return ""

    return jalali_date.strftime("%A")


@register.simple_tag
def jalali_now(format_string='%d %B %Y'):

    now = timezone.now()
    now = timezone.localtime(now)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=now)
    return jalali_date.strftime(format_string)
