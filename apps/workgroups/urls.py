from django.urls import path

from .views import WorkGroupDetailView, WorkGroupListView

app_name = "workgroups"

urlpatterns = [
    path("", WorkGroupListView.as_view(), name="list"),
    path("<str:slug>/", WorkGroupDetailView.as_view(), name="detail"),
]
