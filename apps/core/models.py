from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model providing created/updated timestamps.
    Inherited by models that need audit timestamps.
    Does not create its own database table.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True