from rest_framework import serializers

from .models import InstagramPost


class InstagramPostSerializer(serializers.ModelSerializer):
    """Public, read-only shape used on the homepage."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = InstagramPost
        fields = ["id", "image", "link", "caption", "display_order"]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class InstagramPostAdminSerializer(serializers.ModelSerializer):
    """Admin CRUD shape, with the image as a writable upload field."""

    class Meta:
        model = InstagramPost
        fields = [
            "id", "image", "link", "caption",
            "display_order", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
