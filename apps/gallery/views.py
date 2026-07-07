from rest_framework import generics, permissions

from .models import InstagramPost
from .serializers import InstagramPostSerializer, InstagramPostAdminSerializer


class InstagramPostPublicListView(generics.ListAPIView):
    """Public: active gallery photos, for the homepage."""
    queryset = InstagramPost.objects.filter(is_active=True)
    serializer_class = InstagramPostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class InstagramPostAdminListCreateView(generics.ListCreateAPIView):
    """Admin: view all gallery photos (active or not) and upload new ones."""
    queryset = InstagramPost.objects.all()
    serializer_class = InstagramPostAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None


class InstagramPostAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: edit or delete a single gallery photo."""
    queryset = InstagramPost.objects.all()
    serializer_class = InstagramPostAdminSerializer
    permission_classes = [permissions.IsAdminUser]
