from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "blurb"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["url", "is_primary"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


def _thumbnail_url(obj, context):
    """Shared helper: build an absolute thumbnail URL from a product's first image."""
    primary = obj.images.first()
    if not primary:
        return None
    request = context.get("request")
    return request.build_absolute_uri(primary.image.url) if request else primary.image.url


def _active_discount_price(obj):
    """Only surface discount_price to public serializers while the sale is
    actually active — this is what makes a scheduled discount 'auto-expire'
    without any cleanup job: once discount_ends_on passes, this just starts
    returning None again on its own."""
    return str(obj.discount_price) if obj.is_discount_active else None


class ProductListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    fabric_display = serializers.CharField(source="get_fabric_display", read_only=True)
    # color is free text now (no more Color choices), so there's no
    # auto-generated get_color_display() — just mirror the raw value.
    color_display = serializers.CharField(source="color", read_only=True)
    thumbnail = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(source="is_discount_active", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "name", "categories",
            "price", "discount_price", "is_on_sale",
            "fabric", "fabric_display",
            "color", "color_display",
            "is_featured", "thumbnail", "created_at",
        ]

    def get_thumbnail(self, obj):
        return _thumbnail_url(obj, self.context)

    def get_discount_price(self, obj):
        return _active_discount_price(obj)


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    fabric_display = serializers.CharField(source="get_fabric_display", read_only=True)
    color_display = serializers.CharField(source="color", read_only=True)
    border_color_display = serializers.CharField(source="border_color", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(source="is_discount_active", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "product_code", "name", "categories", "description",
            "price", "discount_price", "is_on_sale",
            "fabric", "fabric_display",
            "color", "color_display",
            "border_color", "border_color_display",
            "status", "is_featured", "is_available",
            "images", "created_at",
        ]

    def get_is_available(self, obj):
        return obj.status == Product.Status.PUBLISHED

    def get_discount_price(self, obj):
        return _active_discount_price(obj)


class WritableCategoryField(serializers.PrimaryKeyRelatedField):
    """Accepts category ids on write, but serializes the full nested
    Category objects on read — the admin UI reads fields like
    `product.categories[].name` directly."""

    def to_representation(self, value):
        return CategorySerializer(value, context=self.context).data


class ProductAdminSerializer(serializers.ModelSerializer):
    categories = WritableCategoryField(many=True, queryset=Category.objects.all())
    images = ProductImageSerializer(many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "slug", "product_code", "name", "categories", "description",
            "price", "discount_price", "discount_starts_on", "discount_ends_on", "quantity",
            "fabric", "color", "border_color",
            "status", "is_featured",
            "images", "thumbnail", "uploaded_images",
            "created_at", "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_thumbnail(self, obj):
        return _thumbnail_url(obj, self.context)

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = super().create(validated_data)
        for index, image_file in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image_file,
                is_primary=(index == 0),
            )
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = super().update(instance, validated_data)
        for index, image_file in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image_file,
                is_primary=(index == 0 and not product.images.exists()),
            )
        return product


class CategoryAdminSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "blurb", "product_count", "created_at"]
        read_only_fields = ["slug", "created_at"]

    def get_product_count(self, obj):
        return obj.products.count()