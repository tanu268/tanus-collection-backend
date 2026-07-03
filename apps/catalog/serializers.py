from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = ProductImage
        fields = ["url", "is_primary"]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    fabric_display = serializers.CharField(source="get_fabric_display", read_only=True)
    color_display = serializers.CharField(source="get_color_display", read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "slug", "name", "category",
            "price", "discount_price",
            "fabric", "fabric_display",
            "color", "color_display",
            "is_featured", "thumbnail", "created_at",
        ]

    def get_thumbnail(self, obj):
        primary = obj.images.first()
        if primary:
            return primary.image.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    fabric_display = serializers.CharField(source="get_fabric_display", read_only=True)
    color_display = serializers.CharField(source="get_color_display", read_only=True)
    border_color_display = serializers.CharField(source="get_border_color_display", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "slug", "product_code", "name", "category", "description",
            "price", "discount_price",
            "fabric", "fabric_display",
            "color", "color_display",
            "border_color", "border_color_display",
            "status", "is_featured", "is_available",
            "images", "created_at",
        ]

    def get_is_available(self, obj):
        return obj.status == Product.Status.PUBLISHED

class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id", "slug", "product_code", "name", "category", "description",
            "price", "discount_price", "quantity",
            "fabric", "color", "border_color",
            "status", "is_featured",
            "created_at", "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]