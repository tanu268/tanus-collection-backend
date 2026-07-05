from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("product", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("product__name", "product__product_code")
    readonly_fields = ("product", "message", "created_at")
    ordering = ("-created_at",)