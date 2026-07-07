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


class SiteSettings(TimeStampedModel):
    """
    Singleton row holding boutique-wide settings (shown on the admin
    Settings page). Always accessed/updated via pk=1 — use
    SiteSettings.load() to get-or-create it instead of querying directly.
    """

    name = models.CharField(max_length=150, default="Tanu's Collection")
    established = models.PositiveIntegerField(default=2012)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    hours = models.CharField(max_length=100, blank=True)
    instagram = models.URLField(blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton — never actually delete the row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site settings"