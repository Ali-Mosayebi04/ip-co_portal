from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.news.models import News, NewsStatus

from .models import SectionLink, SiteInfo


class HomePageTests(TestCase):
    def setUp(self):
        SiteInfo.objects.create(about_text="متن آزمایشی درباره ما")
        SectionLink.objects.create(title="منابع انسانی", url="/hr/", order=1)
        News.objects.create(
            title="خبر آزمایشی",
            summary="خلاصه خبر آزمایشی",
            body="متن کامل خبر آزمایشی",
            status=NewsStatus.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_shows_published_news(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "خبر آزمایشی")

    def test_home_page_hides_draft_news(self):
        News.objects.create(
            title="خبر پیش‌نویس",
            summary="خلاصه",
            body="متن",
            status=NewsStatus.DRAFT,
        )
        response = self.client.get(reverse("home:index"))
        self.assertNotContains(response, "خبر پیش‌نویس")

    def test_home_page_shows_section_links(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "منابع انسانی")

    def test_home_page_shows_site_info_from_context_processor(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "متن آزمایشی درباره ما")
