"""Domain models for the ``workgroups`` app: the company's work groups
(کارگروه‌ها) and the employees that belong to each one."""

from __future__ import annotations

import os
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from common.validators import IMAGE_VALIDATORS


def employee_photo_upload_path(instance: "Employee", filename: str) -> str:
    """Random, collision-free filename for employee photos."""
    ext = os.path.splitext(filename)[1].lower()
    return f"workgroups/employees/{uuid.uuid4().hex}{ext}"


class WorkGroup(models.Model):
    name = models.CharField("نام کارگروه", max_length=100)
    slug = models.SlugField(
        "نامک",
        unique=True,
        allow_unicode=True,
        blank=True,
        help_text="در صورت خالی بودن به‌صورت خودکار از نام ساخته می‌شود.",
    )
    description = models.TextField("توضیحات", blank=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "کارگروه"
        verbose_name_plural = "کارگروه‌ها"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or uuid.uuid4().hex[:10]
            slug = base_slug
            counter = 1
            while WorkGroup.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("workgroups:detail", kwargs={"slug": self.slug})


class Employee(models.Model):
    workgroup = models.ForeignKey(
        WorkGroup,
        on_delete=models.CASCADE,
        related_name="employees",
        verbose_name="کارگروه",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
        verbose_name="حساب کاربری",
        help_text="در صورت اتصال، این کارمند می‌تواند وارد پورتال شده و جلسات پیش رو خود را ببیند.",
    )
    full_name = models.CharField("نام و نام خانوادگی", max_length=150)
    position = models.CharField("سمت", max_length=150, blank=True)
    photo = models.ImageField(
        "عکس",
        upload_to=employee_photo_upload_path,
        blank=True,
        null=True,
        validators=IMAGE_VALIDATORS,
    )
    email = models.EmailField("ایمیل", blank=True)
    phone = models.CharField("تلفن داخلی", max_length=20, blank=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["order", "full_name"]
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"

    def __str__(self) -> str:
        return self.full_name
