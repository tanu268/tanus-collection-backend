from django.db import models

from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class Inquiry(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inquiries",
    )
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"Inquiry about {self.product.product_code}"