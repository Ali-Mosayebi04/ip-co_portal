from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path


def health(_request):
    return HttpResponse("ok")


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("core/", include("apps.core.urls", namespace="core")),
    path("news/", include("apps.news.urls", namespace="news")),
    path("training/", include("apps.training.urls", namespace="training")),
    path("workgroups/", include("apps.workgroups.urls", namespace="workgroups")),
    path("meetings/", include("apps.meetings.urls", namespace="meetings")),
    path("", include("apps.home.urls", namespace="home")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
