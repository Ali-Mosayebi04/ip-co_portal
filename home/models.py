import os
import uuid

from __future__ import annotations
from typing import Optional
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator, URLValidator
from django.db import models, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def validate_image_size(image) -> None:
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"حجم تصویر نباید بیشتر از {MAX_IMAGE_SIZE_MB} مگابایت باشد."
        )


def validate_image_content(image) -> None:
    from PIL import Image, UnidentifiedImageError

    try:
        image.seek(0)
        with Image.open(image) as opened:
            opened.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("فایل انتخاب‌شده یک تصویر معتبر نیست.")
    finally:
        image.seek(0)


IMAGE_VALIDATORS = [
    validate_image_size,
    validate_image_content,
    FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
]


def news_cover_upload_path(instance: "News", filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"news/covers/{uuid.uuid4().hex}{ext}"


def _validate_internal_or_absolute_url(value: str) -> None:
    if not value:
        return
    if value.startswith("/"):
        return
    URLValidator()(value)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        abstract = True


class OrderedLink(TimeStampedModel):
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
    open_in_new_tab = models.BooleanField("باز شدن در تب جدید", default=False)

    class Meta(OrderedLink.Meta):
        verbose_name = "آیتم منوی هدر"
        verbose_name_plural = "منوی هدر"


class SectionLink(OrderedLink):
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
    class Meta(OrderedLink.Meta):
        verbose_name = "لینک سریع فوتر"
        verbose_name_plural = "لینک‌های سریع فوتر"


_SITE_INFO_CACHE_KEY = "home:site_info:v1"
_SITE_INFO_CACHE_TTL_SECONDS = 300


class SiteInfo(TimeStampedModel):
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
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(_SITE_INFO_CACHE_KEY)

    def delete(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def load(cls) -> "SiteInfo":
        obj = cache.get(_SITE_INFO_CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1, defaults={"about_text": ""})
            cache.set(_SITE_INFO_CACHE_KEY, obj, _SITE_INFO_CACHE_TTL_SECONDS)
        return obj


class NewsStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    PUBLISHED = "published", "منتشر شده"


class NewsQuerySet(models.QuerySet):
    def published(self) -> QuerySet:
        return self.filter(
            status=NewsStatus.PUBLISHED,
            published_at__lte=timezone.now(),
        )


class News(TimeStampedModel):
    title = models.CharField("عنوان", max_length=200)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news",
        verbose_name="نویسنده",
    )

    slug = models.SlugField(
        "نامک",
        max_length=220,
        unique=True,
        blank=True,
        allow_unicode=True,
        help_text="در صورت خالی بودن به‌صورت خودکار از عنوان ساخته می‌شود.",
    )

    summary = models.CharField("خلاصه", max_length=300)
    body = models.TextField("متن کامل")

    cover_image = models.ImageField(
        "تصویر شاخص",
        upload_to=news_cover_upload_path,
        blank=True,
        null=True,
        validators=IMAGE_VALIDATORS,
    )

    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=NewsStatus.choices,
        default=NewsStatus.DRAFT,
    )
    published_at = models.DateTimeField("تاریخ انتشار", default=timezone.now)
    views = models.PositiveIntegerField("تعداد بازدید", default=0)

    objects = NewsQuerySet.as_manager()

    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"
        ordering = ["-published_at", "-id"]
        get_latest_by = "published_at"
        indexes = [
            models.Index(
                fields=["status", "-published_at"], name="news_status_pubdate_idx"
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def _build_unique_slug(self) -> str:
        base_slug = slugify(self.title, allow_unicode=True) or uuid.uuid4().hex[:10]
        slug = base_slug
        counter = 1
        while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._build_unique_slug()

        old_cover_name: Optional[str] = None
        if self.pk:
            old_cover_name = (
                News.objects.filter(pk=self.pk)
                .values_list("cover_image", flat=True)
                .first()
            )

        with transaction.atomic():
            super().save(*args, **kwargs)

        new_cover_name = self.cover_image.name if self.cover_image else None
        if old_cover_name and old_cover_name != new_cover_name:
            transaction.on_commit(lambda: default_storage.delete(old_cover_name))

    def delete(self, *args, **kwargs) -> None:
        cover_name = self.cover_image.name if self.cover_image else None
        with transaction.atomic():
            super().delete(*args, **kwargs)
        if cover_name:
            transaction.on_commit(lambda: default_storage.delete(cover_name))

    def get_absolute_url(self) -> str:
        return reverse("home:news-detail", kwargs={"slug": self.slug})
