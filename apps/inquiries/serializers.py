from rest_framework import serializers

from apps.catalog.serializers import ProductDetailSerializer
from .models import Inquiry, InquiryCartItem


class InquiryCartItemSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)

    class Meta:
        model = InquiryCartItem
        fields = ["id", "product", "created_at"]


class InquirySerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    customer_name = serializers.CharField(source="customer.first_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    customer_phone = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            "id", "product", "message", "batch_id", "status", "status_display",
            "customer_name", "customer_email", "customer_phone", "created_at",
        ]
        read_only_fields = [
            "id", "created_at", "batch_id", "customer_name",
            "customer_email", "customer_phone", "status_display",
        ]

    def get_customer_phone(self, obj):
        if not obj.customer:
            return ""
        return getattr(getattr(obj.customer, "profile", None), "phone", "")
