from django.urls import path

from . import views

app_name = "meetings"

urlpatterns = [
    path("upcoming/", views.UpcomingMeetingsView.as_view(), name="upcoming"),
    path("manage/", views.MeetingListView.as_view(), name="list"),
    path("manage/create/", views.MeetingCreateView.as_view(), name="create"),
    path("manage/<int:pk>/", views.MeetingDetailView.as_view(), name="detail"),
    path("manage/<int:pk>/edit/", views.MeetingUpdateView.as_view(), name="edit"),
    path("manage/<int:pk>/delete/", views.MeetingDeleteView.as_view(), name="delete"),
]
