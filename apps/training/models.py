"""Domain models for the ``training`` app: company training courses
(دوره‌های آموزشی) organized into categories."""

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


def course_cover_upload_path(instance: "Course", filename: str) -> str:
    """Random, collision-free filename for course cover images."""
    ext = os.path.splitext(filename)[1].lower()
    return f"training/covers/{uuid.uuid4().hex}{ext}"


class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", "مقدماتی"
    INTERMEDIATE = "intermediate", "متوسط"
    ADVANCED = "advanced", "پیشرفته"


class CourseStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    PUBLISHED = "published", "منتشر شده"


class CourseCategory(models.Model):
    """A grouping for courses, e.g. «ایمنی و بهداشت» یا «مهارت‌های فنی»."""

    name = models.CharField("نام دسته", max_length=100)
    slug = models.SlugField(
        "نامک",
        unique=True,
        allow_unicode=True,
        blank=True,
        help_text="در صورت خالی بودن به‌صورت خودکار از نام ساخته می‌شود.",
    )
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "دسته‌بندی آموزشی"
        verbose_name_plural = "دسته‌بندی‌های آموزشی"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or uuid.uuid4().hex[:10]
            slug = base_slug
            counter = 1
            while (
                CourseCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            ):
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)


class CourseQuerySet(models.QuerySet):
    def published(self) -> "CourseQuerySet":
        """Everything visible to the public: published *and* whose
        scheduled publish time has already passed."""
        return self.filter(
            status=CourseStatus.PUBLISHED,
            published_at__lte=timezone.now(),
        )


class Course(models.Model):
    title = models.CharField("عنوان دوره", max_length=200)

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="دسته‌بندی",
    )

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses_taught",
        verbose_name="مدرس",
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
    description = models.TextField("توضیحات کامل دوره")

    cover_image = models.ImageField(
        "تصویر شاخص",
        upload_to=course_cover_upload_path,
        blank=True,
        null=True,
        validators=IMAGE_VALIDATORS,
    )

    level = models.CharField(
        "سطح دوره",
        max_length=20,
        choices=CourseLevel.choices,
        default=CourseLevel.BEGINNER,
    )
    duration_hours = models.PositiveIntegerField("مدت دوره (ساعت)", default=0)

    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=CourseStatus.choices,
        default=CourseStatus.DRAFT,
    )
    published_at = models.DateTimeField("تاریخ انتشار", default=timezone.now)
    views = models.PositiveIntegerField("تعداد بازدید", default=0)

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    objects = CourseQuerySet.as_manager()

    class Meta:
        verbose_name = "دوره آموزشی"
        verbose_name_plural = "دوره‌های آموزشی"
        ordering = ["-published_at", "-id"]
        get_latest_by = "published_at"
        indexes = [
            models.Index(
                fields=["status", "-published_at"],
                name="training_status_pubdate_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # -- slug -------------------------------------------------------------

    def _build_unique_slug(self) -> str:
        base_slug = slugify(self.title, allow_unicode=True) or uuid.uuid4().hex[:10]
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
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
                Course.objects.filter(pk=self.pk)
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
        return reverse("training:detail", kwargs={"slug": self.slug})
