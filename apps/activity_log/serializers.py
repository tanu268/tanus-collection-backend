from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id", "action", "description", "object_id",
            "content_type_name", "performed_by_name", "created_at",
        ]

    def get_performed_by_name(self, obj):
        if not obj.performed_by:
            return "System"
        return obj.performed_by.first_name or obj.performed_by.username