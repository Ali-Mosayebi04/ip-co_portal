from django.urls import path

from . import views

app_name = "meetings"

urlpatterns = [
    path("upcoming/", views.UpcomingMeetingsView.as_view(), name="upcoming"),
]
