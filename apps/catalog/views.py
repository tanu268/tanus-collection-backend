from rest_framework.response import Response
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import Category, Product

from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework import viewsets, permissions
from .serializers import ProductAdminSerializer
from .serializers import (
    CategorySerializer,
    CategoryAdminSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)

from rest_framework.views import APIView
from apps.activity_log.models import ActivityLog
from apps.activity_log.serializers import ActivityLogSerializer


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__slug")
    featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Product
        fields = ["fabric", "color", "category", "featured", "min_price", "max_price"]


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "product_code"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Product.objects.public().select_related("category").prefetch_related("images")


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.public().select_related("category").prefetch_related("images")


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"



class ProductAdminViewSet(viewsets.ModelViewSet):
    serializer_class = ProductAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all().select_related("category").prefetch_related("images")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "category", "fabric", "color", "is_featured"]
    search_fields = ["name", "product_code"]
    ordering_fields = ["price", "created_at", "name", "quantity"]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.status = Product.Status.ARCHIVED
        product.save()
        return Response(status=204)

class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        products = Product.objects.all()
        data = {
            "total_products": products.count(),
            "available_products": products.filter(status=Product.Status.PUBLISHED).count(),
            "sold_out_products": products.filter(status=Product.Status.SOLD_OUT).count(),
            "hidden_products": products.filter(status=Product.Status.HIDDEN).count(),
            "draft_products": products.filter(status=Product.Status.DRAFT).count(),
            "archived_products": products.filter(status=Product.Status.ARCHIVED).count(),
            "featured_products": products.filter(is_featured=True).count(),
            "recent_activity": ActivityLogSerializer(
                ActivityLog.objects.all()[:5], many=True
            ).data,
        }
        return Response(data)

class CategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # for image upload