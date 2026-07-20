from django.views.generic import TemplateView


class CoreHomeView(TemplateView):
    template_name = "core/home.html"
