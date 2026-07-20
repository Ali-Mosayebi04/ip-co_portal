"""Views for the ``home`` app: the company home page and the (temporary)
news detail page."""

from __future__ import annotations

from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView

from .models import NavItem, News, QuickLink, SectionLink, SiteInfo

LATEST_NEWS_COUNT = 6

# Fields the home page template actually reads. Restricting the query to
# these columns keeps the "latest news" list light, especially once
# ``body`` grows to hold full article text.
_NEWS_LIST_FIELDS = ("id", "title", "slug", "summary", "cover_image", "published_at")


class HomeView(TemplateView):
    """Company home page: about section, latest news, the eight section
    links, header nav and footer quick links."""

    template_name = "home/home.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "site_info": SiteInfo.load(),
                "nav_items": self._get_nav_items(),
                "section_links": self._get_section_links(),
                "quick_links": self._get_quick_links(),
                "latest_news": self._get_latest_news(),
            }
        )
        return context

    @staticmethod
    def _get_nav_items() -> QuerySet[NavItem]:
        return NavItem.objects.filter(is_active=True)

    @staticmethod
    def _get_section_links() -> QuerySet[SectionLink]:
        return SectionLink.objects.filter(is_active=True)

    @staticmethod
    def _get_quick_links() -> QuerySet[QuickLink]:
        return QuickLink.objects.filter(is_active=True)

    @staticmethod
    def _get_latest_news() -> QuerySet[News]:
        return News.objects.published().only(*_NEWS_LIST_FIELDS)[:LATEST_NEWS_COUNT]


class NewsDetailView(DetailView):
    """Public news detail page.

    Only ever exposes published news, even to someone who guesses or
    shares a slug for a draft, and records a view atomically at the
    database level so concurrent hits never clobber each other's count.

    Will move to a dedicated ``news`` app once that part of the project
    is scaffolded.
    """

    model = News
    template_name = "home/news_detail.html"
    context_object_name = "news_item"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[News]:
        return News.objects.published().select_related("author")

    def get_object(self, queryset: QuerySet[News] | None = None) -> News:
        queryset = queryset or self.get_queryset()
        obj = get_object_or_404(queryset, slug=self.kwargs["slug"])
        self._record_view(obj)
        return obj

    @staticmethod
    def _record_view(news_item: News) -> None:
        """Increment the view counter with a single atomic UPDATE
        (``F('views') + 1``) instead of read-modify-write in Python, so
        two simultaneous requests can never overwrite each other's
        increment."""
        News.objects.filter(pk=news_item.pk).update(views=F("views") + 1)
        news_item.refresh_from_db(fields=["views"])