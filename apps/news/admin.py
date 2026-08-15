from django.contrib import admin
from django.utils.html import format_html

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "published_at",
        "views",
        "cover_preview",
    )
    list_filter = ("status", "published_at", "author")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at", "updated_at", "views", "cover_preview")
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "summary", "body")}),
        ("رسانه", {"fields": ("cover_image", "cover_preview")}),
        ("انتشار", {"fields": ("status", "published_at")}),
        ("آمار و اطلاعات سیستمی", {"fields": ("views", "created_at", "updated_at")}),
    )

    @admin.display(description="پیش‌نمایش")
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:6px;" />',
                obj.cover_image.url,
            )
        return "—"

    def save_model(self, request, obj, form, change):
        if not change and not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
