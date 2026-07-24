from django.urls import path

from . import views

app_name = "training"

urlpatterns = [
    path("", views.CourseListView.as_view(), name="list"),
    path("<str:slug>/", views.CourseDetailView.as_view(), name="detail"),
]
