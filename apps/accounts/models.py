from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class Profile(TimeStampedModel):
    """Extra customer fields not on Django's built-in User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile for {self.user}"


class WishlistItem(TimeStampedModel):
    """A product a logged-in customer has saved to their wishlist."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} wishlisted {self.product.product_code}"
