import uuid
from datetime import timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from .models import Inquiry, InquiryCartItem
from .serializers import InquiryCartItemSerializer, InquirySerializer


# --- Inquiry cart (pending, pre-submission) ------------------------------
# Identifies products by slug, matching how the storefront already
# references products everywhere.

class InquiryCartListView(generics.ListAPIView):
    """Authenticated: view your pending inquiry cart."""
    serializer_class = InquiryCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            InquiryCartItem.objects.filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__categories", "product__images")
        )


class InquiryCartAddView(APIView):
    """Authenticated: add a product (by slug) to your inquiry cart."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        slug = request.data.get("product")
        if not slug:
            return Response({"detail": "product (slug) is required."}, status=400)
        product = get_object_or_404(Product, slug=slug)
        item, created = InquiryCartItem.objects.get_or_create(user=request.user, product=product)
        return Response(
            InquiryCartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InquiryCartRemoveView(APIView):
    """Authenticated: remove a product (by slug) from your inquiry cart."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug):
        InquiryCartItem.objects.filter(user=request.user, product__slug=slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InquiryCartClearView(APIView):
    """Authenticated: empty your inquiry cart without submitting."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        InquiryCartItem.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Submit ---------------------------------------------------------------

class InquirySubmitView(APIView):
    """
    Authenticated: turn the current inquiry cart into real Inquiry records
    (one per product, sharing a batch_id so admins can see them as one
    submission), then clear the cart.
    
    Can accept:
    - items: list of product slugs (will add to cart and submit)
    - message: optional message text
    - customer_name, customer_email: ignored (used from authenticated user)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # If items are provided in request, add them to cart first
        items = request.data.get("items", [])
        if items:
            for slug in items:
                product = get_object_or_404(Product, slug=slug)
                InquiryCartItem.objects.get_or_create(user=request.user, product=product)
        
        cart_items = list(
            InquiryCartItem.objects.filter(user=request.user).select_related("product")
        )
        if not cart_items:
            return Response({"detail": "Your inquiry cart is empty."}, status=400)

        message = request.data.get("message", "")
        batch_id = uuid.uuid4()

        created = Inquiry.objects.bulk_create([
            Inquiry(customer=request.user, product=item.product, message=message, batch_id=batch_id)
            for item in cart_items
        ])

        InquiryCartItem.objects.filter(user=request.user).delete()

        return Response(
            InquirySerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class InquiryAdminListView(generics.ListAPIView):
    """Admin: view all customer inquiries, read-only."""
    queryset = Inquiry.objects.all().select_related("product", "customer", "customer__profile")
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]


class InquiryAdminStatusUpdateView(APIView):
    """Admin: update the status of a single inquiry."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        inquiry = get_object_or_404(Inquiry, pk=pk)
        status_value = request.data.get("status")
        valid_statuses = [choice[0] for choice in Inquiry.Status.choices]
        if status_value not in valid_statuses:
            return Response({"detail": f"status must be one of {valid_statuses}."}, status=400)
        inquiry.status = status_value
        inquiry.save(update_fields=["status"])
        return Response(InquirySerializer(inquiry).data)


class InquiryAnalyticsByCategoryView(APIView):
    """Admin: count of inquiries per product category, last 30 days."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        since = timezone.now() - timedelta(days=30)
        rows = (
            Inquiry.objects.filter(created_at__gte=since)
            .values("product__categories__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        data = [
            {"category": row["product__categories__name"] or "Uncategorized", "count": row["count"]}
            for row in rows
        ]
        return Response(data)
