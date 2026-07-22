"""Domain models for the ``home`` app.

Everything the company home page needs to render *besides* the news
feed (see ``apps.news``) and the work-group directory (see
``apps.workgroups``): the "about us" block, header navigation, the
eight links to other company sections, and the footer quick links.
"""

from __future__ import annotations

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

from common.validators import IMAGE_VALIDATORS


def _validate_internal_or_absolute_url(value: str) -> None:
    """A link must be either an internal path (``/hr/``) or a full,
    well-formed absolute URL. Used by :class:`OrderedLink` subclasses."""
    if not value:
        return
    if value.startswith("/"):
        return
    URLValidator()(value)  # raises ValidationError on its own


class TimeStampedModel(models.Model):
    """Abstract base holding created/updated timestamps."""

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        abstract = True


class OrderedLink(TimeStampedModel):
    """Abstract base for simple orderable link blocks: nav items,
    section cards, footer quick links, etc."""

    title = models.CharField("عنوان", max_length=100)
    url = models.CharField(
        "آدرس",
        max_length=300,
        help_text="یک مسیر داخلی (مثلاً /news/) یا یک آدرس کامل معتبر.",
    )
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        try:
            _validate_internal_or_absolute_url(self.url)
        except ValidationError:
            raise ValidationError(
                {"url": "آدرس باید یک مسیر داخلی (شروع با /) یا یک URL معتبر باشد."}
            )


class NavItem(OrderedLink):
    """Extra, manually managed header links (e.g. اخبار / آموزش).

    The "کارگروه‌ها" (work groups) entry is *not* one of these — it is
    rendered separately in the header as a live dropdown sourced from
    ``apps.workgroups`` (see ``apps/workgroups/context_processors.py``),
    since its options change whenever work groups are added or removed.
    """

    open_in_new_tab = models.BooleanField("باز شدن در تب جدید", default=False)

    class Meta(OrderedLink.Meta):
        verbose_name = "آیتم منوی هدر"
        verbose_name_plural = "منوی هدر"


class SectionLink(OrderedLink):
    """The eight links to other company sections shown on the home page."""

    icon = models.CharField(
        "کلاس آیکون",
        max_length=100,
        blank=True,
        help_text="مثلاً یک کلاس آیکون Bootstrap Icons، مانند bi-people",
    )
    description = models.CharField("توضیح کوتاه", max_length=200, blank=True)

    class Meta(OrderedLink.Meta):
        verbose_name = "لینک بخش شرکت"
        verbose_name_plural = "لینک‌های بخش‌های شرکت"


class QuickLink(OrderedLink):
    """Footer quick links."""

    class Meta(OrderedLink.Meta):
        verbose_name = "لینک سریع فوتر"
        verbose_name_plural = "لینک‌های سریع فوتر"


# ---------------------------------------------------------------------------
# Site info (singleton)
# ---------------------------------------------------------------------------

_SITE_INFO_CACHE_KEY = "home:site_info:v1"
_SITE_INFO_CACHE_TTL_SECONDS = 300


class SiteInfo(TimeStampedModel):
    """Singleton row holding the "about us" content and contact info
    shown on the home page and in the footer.

    Reads go through the default cache to keep every page (not just the
    home page — the footer needs this too) from hitting the database on
    every single request just to fetch mostly static content; writes
    invalidate the cache immediately.
    """

    about_title = models.CharField(
        "عنوان درباره ما", max_length=150, default="درباره ایران خودرو"
    )
    about_text = models.TextField("متن درباره ما")
    logo = models.ImageField(
        "لوگو",
        upload_to="site/",
        blank=True,
        null=True,
        validators=IMAGE_VALIDATORS,
    )
    phone = models.CharField("تلفن", max_length=20, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    address = models.CharField("آدرس", max_length=300, blank=True)

    class Meta:
        verbose_name = "اطلاعات سایت"
        verbose_name_plural = "اطلاعات سایت"

    def __str__(self) -> str:
        return self.about_title

    def save(self, *args, **kwargs) -> None:
        # Enforce a single row (singleton pattern) without a raw SQL hack.
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(_SITE_INFO_CACHE_KEY)

    def delete(self, *args, **kwargs) -> None:
        # Prevent accidental deletion of the only site-info row.
        pass

    @classmethod
    def load(cls) -> "SiteInfo":
        obj = cache.get(_SITE_INFO_CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1, defaults={"about_text": ""})
            cache.set(_SITE_INFO_CACHE_KEY, obj, _SITE_INFO_CACHE_TTL_SECONDS)
        return obj
