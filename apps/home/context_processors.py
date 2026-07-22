"""Template context processors for ``apps.home``.

Registered in ``config.settings.TEMPLATES``. This makes the header and
footer partials work the same way on *every* page — home, news,
work-group listings, etc. — without each view having to remember to
pass ``site_info``/``nav_items``/``quick_links`` into its context.
"""

from __future__ import annotations

from django.http import HttpRequest

from .models import NavItem, QuickLink, SiteInfo


def site_globals(request: HttpRequest) -> dict:
    return {
        "site_info": SiteInfo.load(),
        "nav_items": NavItem.objects.filter(is_active=True),
        "quick_links": QuickLink.objects.filter(is_active=True),
    }
