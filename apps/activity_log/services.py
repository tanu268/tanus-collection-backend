from django.contrib.contenttypes.models import ContentType

from .models import ActivityLog


def log_activity(instance, action, description="", performed_by=None):
    ActivityLog.objects.create(
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        action=action,
        description=description,
        performed_by=performed_by,
    )