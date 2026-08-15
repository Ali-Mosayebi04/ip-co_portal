from __future__ import annotations

from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import News

PAGE_SIZE = 6
_NEWS_LIST_FIELDS = ("id", "title", "slug", "summary", "cover_image", "published_at")


class NewsListView(ListView):

    model = News
    template_name = "news/list.html"
    context_object_name = "news_list"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[News]:
        queryset = News.objects.published().only(*_NEWS_LIST_FIELDS)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(summary__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = "news/detail.html"
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

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        news_item: News = context["news_item"]

        word_count = len(news_item.body.split())
        context["reading_minutes"] = max(1, round(word_count / 180))

        context["related_news"] = (
            News.objects.published()
            .exclude(pk=news_item.pk)
            .only(*_NEWS_LIST_FIELDS)
            .order_by("-published_at")[:3]
        )
        return context

    @staticmethod
    def _record_view(news_item: News) -> None:
        News.objects.filter(pk=news_item.pk).update(views=F("views") + 1)
        news_item.refresh_from_db(fields=["views"])
