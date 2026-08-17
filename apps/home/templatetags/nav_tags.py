from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def nav_active(request_path: str, url: str) -> bool:

    if not url:
        return False

    normalized_url = url.rstrip("/") or "/"
    normalized_path = request_path.rstrip("/") or "/"

    if normalized_url == "/":
        return normalized_path == "/"

    return normalized_path == normalized_url or normalized_path.startswith(
        normalized_url + "/"
    )
