from rest_framework import generics, permissions
from .models import Inquiry
from .serializers import InquirySerializer


class InquiryCreateView(generics.CreateAPIView):
    """Public: customers submit WhatsApp inquiries."""
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer


class InquiryAdminListView(generics.ListAPIView):
    """Admin: view all customer inquiries, read-only."""
    queryset = Inquiry.objects.all().select_related("product")
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]