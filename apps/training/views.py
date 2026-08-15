from __future__ import annotations

from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Course, CourseCategory

PAGE_SIZE = 12
_COURSE_LIST_FIELDS = (
    "id",
    "title",
    "slug",
    "summary",
    "cover_image",
    "level",
    "duration_hours",
    "published_at",
    "category",
)


class CourseListView(ListView):

    model = Course
    template_name = "training/list.html"
    context_object_name = "courses"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Course]:
        queryset = Course.objects.published().select_related("category").only(
            *_COURSE_LIST_FIELDS
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(summary__icontains=query)
            )

        category_slug = self.request.GET.get("category", "").strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["active_category"] = self.request.GET.get("category", "").strip()
        context["categories"] = CourseCategory.objects.all()
        context["training_pagination_extra"] = (
            f"&category={context['active_category']}" if context["active_category"] else ""
        )
        return context


class CourseDetailView(DetailView):

    model = Course
    template_name = "training/detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[Course]:
        return Course.objects.published().select_related("category", "instructor")

    def get_object(self, queryset: QuerySet[Course] | None = None) -> Course:
        queryset = queryset or self.get_queryset()
        obj = get_object_or_404(queryset, slug=self.kwargs["slug"])
        self._record_view(obj)
        return obj

    @staticmethod
    def _record_view(course: Course) -> None:

        Course.objects.filter(pk=course.pk).update(views=F("views") + 1)
        course.refresh_from_db(fields=["views"])
