# apps/catalog/services.py

from .models import Product


def sync_status_with_quantity(product: Product) -> None:
    """
    Business rule: if quantity is zero, status must be Sold Out.
    If quantity becomes positive again and status was Sold Out,
    revert to Published (assumes restocking implies it should be visible again).
    """
    if product.quantity == 0 and product.status != Product.Status.SOLD_OUT:
        product.status = Product.Status.SOLD_OUT
    elif product.quantity > 0 and product.status == Product.Status.SOLD_OUT:
        product.status = Product.Status.PUBLISHED