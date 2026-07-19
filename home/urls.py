from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.HomeView.as_view(), name="index"),
    path("news/<str:slug>/", views.NewsDetailView.as_view(), name="news-detail"),
]
