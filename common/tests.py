import datetime

import jdatetime
from django.test import TestCase
from django.utils import timezone

from common.templatetags.jalali_tags import (
    jalali,
    jalali_day,
    jalali_month,
    jalali_weekday,
    jalali_year,
)


class JalaliTemplateTagTests(TestCase):
    def test_jalali_filters_support_date_values(self):
        value = datetime.date(2026, 7, 31)
        expected = jdatetime.date.fromgregorian(date=value)

        self.assertEqual(jalali(value), expected.strftime('%d %B %Y'))
        self.assertEqual(jalali_day(value), expected.day)
        self.assertEqual(jalali_month(value), expected.strftime('%B'))
        self.assertEqual(jalali_year(value), expected.year)
        self.assertEqual(jalali_weekday(value), expected.strftime('%A'))

    def test_jalali_filters_support_naive_datetime_values(self):
        value = datetime.datetime(2026, 7, 31, 12, 45, 30)
        expected_datetime = timezone.localtime(timezone.make_aware(value))
        expected = jdatetime.datetime.fromgregorian(datetime=expected_datetime)

        self.assertEqual(jalali(value, '%d %B %Y - %H:%M:%S'), expected.strftime('%d %B %Y - %H:%M:%S'))
        self.assertEqual(jalali_day(value), expected.day)
        self.assertEqual(jalali_month(value), expected.strftime('%B'))
        self.assertEqual(jalali_year(value), expected.year)
        self.assertEqual(jalali_weekday(value), expected.strftime('%A'))
