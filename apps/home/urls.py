from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.HomeView.as_view(), name="index"),
    path("about-company/", views.AboutCompanyView.as_view(), name="about_company"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
