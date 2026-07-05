import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class InquiryCartItem(TimeStampedModel):
    """A product a logged-in customer intends to inquire about, before sending."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inquiry_cart_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="in_inquiry_carts",
    )

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} is considering {self.product.product_code}"


class Inquiry(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REPLIED = "replied", "Replied"
        CONFIRMED = "confirmed", "Confirmed"
        CLOSED = "closed", "Closed"

    # null=True keeps this migration-safe if any Inquiry rows already exist
    # without a customer attached.
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inquiries",
        null=True,
    )
    # Multiple products submitted together (one WhatsApp inquiry) share a
    # batch_id, so admins can see them as a single customer submission.
    batch_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inquiries",
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"Inquiry about {self.product.product_code}"
