from django.contrib import admin
from django.utils.html import format_html

from .models import NavItem, News, QuickLink, SectionLink, SiteInfo


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "cover_preview")
    list_filter = ("published_at", "status")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at", "cover_preview")
    fieldsets = (
    (None, {"fields": ("title", "slug", "summary", "body")}),
    ("رسانه", {"fields": ("cover_image", "cover_preview")}),
    ("انتشار", {"fields": ("status", "published_at")}),
    ("اطلاعات سیستمی", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="پیش‌نمایش")
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:6px;" />',
                obj.cover_image.url,
            )
        return "—"


class OrderedLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "url")
    ordering = ("order",)


@admin.register(NavItem)
class NavItemAdmin(OrderedLinkAdmin):
    list_display = OrderedLinkAdmin.list_display + ("open_in_new_tab",)


@admin.register(SectionLink)
class SectionLinkAdmin(OrderedLinkAdmin):
    list_display = OrderedLinkAdmin.list_display + ("icon",)


@admin.register(QuickLink)
class QuickLinkAdmin(OrderedLinkAdmin):
    pass


@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ("about_title", "phone", "email", "updated_at")

    def has_add_permission(self, request):
        # Singleton: block adding a second row once one exists.
        return not SiteInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
