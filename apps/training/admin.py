from django.contrib import admin
from django.utils.html import format_html

from .models import Course, CourseCategory


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "course_count")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="تعداد دوره‌ها")
    def course_count(self, obj):
        return obj.courses.count()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "instructor",
        "level",
        "status",
        "published_at",
        "views",
        "cover_preview",
    )
    list_filter = ("status", "level", "category", "published_at")
    search_fields = ("title", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    autocomplete_fields = ("instructor", "category")
    readonly_fields = ("created_at", "updated_at", "views", "cover_preview")
    fieldsets = (
        (
            None,
            {"fields": ("title", "slug", "category", "instructor", "summary", "description")},
        ),
        ("رسانه", {"fields": ("cover_image", "cover_preview")}),
        ("مشخصات دوره", {"fields": ("level", "duration_hours")}),
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
        # Auto-assign the current staff user as the instructor on first
        # save, so editors never have to pick themselves manually.
        if not change and not obj.instructor_id:
            obj.instructor = request.user
        super().save_model(request, obj, form, change)
