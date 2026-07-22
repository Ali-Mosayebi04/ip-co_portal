from django.contrib import admin

from .models import Announcement, NavItem, QuickLink, SectionLink, SiteInfo


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


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    search_fields = ("title",)
    list_filter = ("is_active",)
    ordering = ("-created_at",)


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
