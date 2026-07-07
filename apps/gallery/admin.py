from django.contrib import admin
from .models import InstagramPost


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ("caption", "display_order", "is_active", "created_at")
    list_filter = ("is_active",)
    ordering = ("display_order", "-created_at")
