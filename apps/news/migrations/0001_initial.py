from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

import apps.news.models


class Migration(migrations.Migration):
    """Move ``News`` from ``apps.home`` into its own app.

    This is a *state-only* migration: it only tells Django's migration
    state that ``News`` now belongs to ``apps.news``. No database
    operations run here, because ``News.Meta.db_table`` is pinned to
    ``"home_news"`` — the table apps.home's original migration already
    created. That means this move is 100% safe for any existing data:
    nothing gets renamed, copied, dropped, or recreated at the database
    level. See apps/home/migrations for the matching state-only
    ``DeleteModel``.
    """

    initial = True

    dependencies = [
        ("home", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="News",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "title",
                            models.CharField(max_length=200, verbose_name="عنوان"),
                        ),
                        (
                            "slug",
                            models.SlugField(
                                allow_unicode=True,
                                blank=True,
                                help_text="در صورت خالی بودن به‌صورت خودکار از عنوان ساخته می‌شود.",
                                max_length=220,
                                unique=True,
                                verbose_name="نامک",
                            ),
                        ),
                        (
                            "summary",
                            models.CharField(max_length=300, verbose_name="خلاصه"),
                        ),
                        ("body", models.TextField(verbose_name="متن کامل")),
                        (
                            "cover_image",
                            models.ImageField(
                                blank=True,
                                null=True,
                                upload_to=apps.news.models.news_cover_upload_path,
                                verbose_name="تصویر شاخص",
                            ),
                        ),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("draft", "پیش‌نویس"),
                                    ("published", "منتشر شده"),
                                ],
                                default="draft",
                                max_length=20,
                                verbose_name="وضعیت",
                            ),
                        ),
                        (
                            "published_at",
                            models.DateTimeField(
                                default=django.utils.timezone.now,
                                verbose_name="تاریخ انتشار",
                            ),
                        ),
                        (
                            "views",
                            models.PositiveIntegerField(
                                default=0, verbose_name="تعداد بازدید"
                            ),
                        ),
                        (
                            "created_at",
                            models.DateTimeField(
                                auto_now_add=True, verbose_name="تاریخ ایجاد"
                            ),
                        ),
                        (
                            "updated_at",
                            models.DateTimeField(
                                auto_now=True, verbose_name="تاریخ بروزرسانی"
                            ),
                        ),
                        (
                            "author",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name="news",
                                to=settings.AUTH_USER_MODEL,
                                verbose_name="نویسنده",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "خبر",
                        "verbose_name_plural": "اخبار",
                        "db_table": "home_news",
                        "ordering": ["-published_at", "-id"],
                        "get_latest_by": "published_at",
                    },
                ),
                migrations.AddIndex(
                    model_name="news",
                    index=models.Index(
                        fields=["status", "-published_at"],
                        name="news_status_pubdate_idx",
                    ),
                ),
            ],
        ),
    ]
