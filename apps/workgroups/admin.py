from django.contrib import admin

from .models import Employee, WorkGroup


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1
    fields = ("full_name", "position", "photo", "email", "phone", "order")
    ordering = ("order", "full_name")


@admin.register(WorkGroup)
class WorkGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "employee_count", "order", "created_at")
    list_editable = ("order",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [EmployeeInline]

    @admin.display(description="تعداد کارمندان")
    def employee_count(self, obj):
        return obj.employees.count()


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "workgroup",
        "position",
        "email",
        "phone",
        "user",
        "order",
    )
    list_filter = ("workgroup",)
    search_fields = ("full_name", "position", "email")
    autocomplete_fields = ("workgroup", "user")
    ordering = ("workgroup", "order", "full_name")
    fields = (
        "workgroup",
        "full_name",
        "position",
        "photo",
        "email",
        "phone",
        "order",
        "user",
    )
