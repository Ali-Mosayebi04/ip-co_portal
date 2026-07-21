from django.urls import path

from .views import WorkGroupDetailView, WorkGroupListView

app_name = "workgroups"

urlpatterns = [
    path("", WorkGroupListView.as_view(), name="list"),
    # str, not the built-in slug converter: WorkGroup.slug allows unicode
    # (Persian) characters, which the ASCII-only slug converter rejects.
    path("<str:slug>/", WorkGroupDetailView.as_view(), name="detail"),
]
