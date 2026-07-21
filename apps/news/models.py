"""Domain model for the ``news`` app: company news articles."""

from __future__ import annotations

import os
import uuid
from typing import Optional

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from common.validators import IMAGE_VALIDATORS


def news_cover_upload_path(instance: "News", filename: str) -> str:
    """Store news covers under a random UUID name.

    This avoids both path traversal from a hostile filename and
    collisions between unrelated uploads that happen to share a name.
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"news/covers/{uuid.uuid4().hex}{ext}"


class NewsStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    PUBLISHED = "published", "منتشر شده"


class NewsQuerySet(models.QuerySet):
    def published(self) -> "NewsQuerySet":
        """Everything visible to the public: published *and* whose
        scheduled publish time has already passed."""
        return self.filter(
            status=NewsStatus.PUBLISHED,
            published_at__lte=timezone.now(),
        )


class News(models.Model):
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

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    objects = NewsQuerySet.as_manager()

    class Meta:
        # Keep pointing at the table this model already had while it
        # lived in ``apps.home``, so moving the app doesn't require any
        # data migration — see apps/news/migrations/0001_initial.py.
        db_table = "home_news"
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

    # -- slug -------------------------------------------------------------

    def _build_unique_slug(self) -> str:
        base_slug = slugify(self.title, allow_unicode=True) or uuid.uuid4().hex[:10]
        slug = base_slug
        counter = 1
        while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug

    # -- persistence --------------------------------------------------------

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
        return reverse("news:detail", kwargs={"slug": self.slug})
