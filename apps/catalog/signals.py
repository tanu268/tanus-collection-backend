# apps/catalog/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from apps.activity_log.services import log_activity


@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    if created:
        log_activity(instance, action="created", description=f"Product '{instance.name}' added to catalog.")
    else:
        log_activity(instance, action="updated", description=f"Product '{instance.name}' was updated.")