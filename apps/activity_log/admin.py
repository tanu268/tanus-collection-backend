from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "content_type", "object_id", "performed_by", "created_at")
    list_filter = ("action", "content_type")
    readonly_fields = ("content_type", "object_id", "action", "description", "performed_by", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False