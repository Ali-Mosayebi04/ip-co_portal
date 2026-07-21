"""Registered in ``config.settings.TEMPLATES`` so the header's
"کارگروه‌ها" dropdown always has the current list of work groups,
regardless of which app rendered the page."""

from __future__ import annotations

from django.http import HttpRequest

from .models import WorkGroup


def workgroups_nav(request: HttpRequest) -> dict:
    return {
        "workgroups_nav": WorkGroup.objects.only("id", "name", "slug"),
    }
