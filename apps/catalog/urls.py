from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryDetailView,
    ProductAdminViewSet,
    AdminDashboardView,
)

router = DefaultRouter()
router.register("admin/products", ProductAdminViewSet, basename="admin-product")


urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
] + router.urls