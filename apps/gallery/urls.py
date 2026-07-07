from django.urls import path
from .views import (
    InstagramPostPublicListView,
    InstagramPostAdminListCreateView,
    InstagramPostAdminDetailView,
)

urlpatterns = [
    path("instagram-posts/", InstagramPostPublicListView.as_view(), name="instagram-posts-public"),
    path("admin/instagram-posts/", InstagramPostAdminListCreateView.as_view(), name="instagram-posts-admin-list"),
    path("admin/instagram-posts/<int:pk>/", InstagramPostAdminDetailView.as_view(), name="instagram-posts-admin-detail"),
]
