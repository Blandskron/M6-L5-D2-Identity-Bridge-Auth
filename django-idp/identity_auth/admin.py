from django.contrib import admin

from .models import EducationalResource


@admin.register(EducationalResource)
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "description", "created_by__username")
    readonly_fields = ("created_at",)
