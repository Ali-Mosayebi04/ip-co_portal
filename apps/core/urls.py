from django.urls import path

from .views import CoreHomeView

app_name = "core"

urlpatterns = [
    path("", CoreHomeView.as_view(), name="home"),
]
