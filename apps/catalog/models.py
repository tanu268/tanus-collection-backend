from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=Product.Status.PUBLISHED)

class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        SOLD_OUT = "sold_out", "Sold Out"
        HIDDEN = "hidden", "Hidden"
        ARCHIVED = "archived", "Archived"

    class Fabric(models.TextChoices):
        SILK = "silk", "Silk"
        COTTON = "cotton", "Cotton"
        GEORGETTE = "georgette", "Georgette"
        CHIFFON = "chiffon", "Chiffon"
        # add more as the business needs them

    class Color(models.TextChoices):
        RED = "red", "Red"
        MAROON = "maroon", "Maroon"
        PINK = "pink", "Pink"
        ORANGE = "orange", "Orange"
        YELLOW = "yellow", "Yellow"
        GOLD = "gold", "Gold"
        GREEN = "green", "Green"
        BLUE = "blue", "Blue"
        NAVY_BLUE = "navy_blue", "Navy Blue"
        PURPLE = "purple", "Purple"
        BLACK = "black", "Black"
        WHITE = "white", "White"
        CREAM = "cream", "Cream"
        GREY = "grey", "Grey"
        MULTICOLOR = "multicolor", "Multicolor"

    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    product_code = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    quantity = models.PositiveIntegerField(default=0)

    fabric = models.CharField(
        max_length=20, choices=Fabric.choices, db_index=True
    )
    color = models.CharField(
        max_length=20, choices=Color.choices, db_index=True
    )
    border_color = models.CharField(
        max_length=20, choices=Color.choices, blank=True, null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_code} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.product_code}")

        from .services import sync_status_with_quantity
        sync_status_with_quantity(self)

        super().save(*args, **kwargs)

class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/%Y/%m/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "created_at"]

    def __str__(self):
        return f"Image for {self.product.product_code} ({'primary' if self.is_primary else 'secondary'})"

