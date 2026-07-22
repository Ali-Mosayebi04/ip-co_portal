"""Views for the ``home`` app: just the company home page.

``site_info``, ``nav_items`` and ``quick_links`` are supplied to every
template by ``apps.home.context_processors.site_globals`` (registered
in settings), so this view only adds what's specific to the home page
itself: the section links grid and the latest-news preview.
"""

from __future__ import annotations

from django.db.models import QuerySet
from django.views.generic import TemplateView

from apps.news.models import News

from .models import SectionLink

LATEST_NEWS_COUNT = 6

# Fields the home page template actually reads. Restricting the query to
# these columns keeps the "latest news" preview light, especially once
# ``body`` grows to hold full article text.
_NEWS_LIST_FIELDS = ("id", "title", "slug", "summary", "cover_image", "published_at")


class HomeView(TemplateView):
    """Company home page: about section, latest news preview, and the
    eight section links. Header/footer content comes from the shared
    context processor."""

    template_name = "home/home.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "section_links": self._get_section_links(),
                "latest_news": self._get_latest_news(),
            }
        )
        return context

    @staticmethod
    def _get_section_links() -> QuerySet[SectionLink]:
        return SectionLink.objects.filter(is_active=True)

    @staticmethod
    def _get_latest_news() -> QuerySet[News]:
        return News.objects.published().only(*_NEWS_LIST_FIELDS)[:LATEST_NEWS_COUNT]
