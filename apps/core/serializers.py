from rest_framework import serializers
from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "name", "established", "phone", "whatsapp_number",
            "email", "address", "hours", "instagram", "updated_at",
        ]
