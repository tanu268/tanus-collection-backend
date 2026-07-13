from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from .models import WishlistItem
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, WishlistItemSerializer


class RegisterView(generics.CreateAPIView):
    """Public: create a customer account and return an auth token."""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Public: exchange email/password for an auth token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    """Authenticated: invalidate the current token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Authenticated: return the current customer's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# --- Wishlist -----------------------------------------------------------
# All wishlist endpoints identify products by slug (not numeric id), since
# that's the identifier already used everywhere on the storefront.

class WishlistListView(generics.ListAPIView):
    """Authenticated: view your saved wishlist."""
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__categories", "product__images")
        )


class WishlistAddView(APIView):
    """Authenticated: add a product (by slug) to your wishlist."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        slug = request.data.get("product")
        if not slug:
            return Response({"detail": "product (slug) is required."}, status=400)
        product = get_object_or_404(Product, slug=slug)
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response(
            WishlistItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class WishlistRemoveView(APIView):
    """Authenticated: remove a product (by slug) from your wishlist."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug):
        WishlistItem.objects.filter(user=request.user, product__slug=slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
