from django.urls import path
from .views import InquiryCreateView, InquiryAdminListView

urlpatterns = [
    path("inquiries/", InquiryCreateView.as_view(), name="inquiry-create"),
    path("admin/inquiries/", InquiryAdminListView.as_view(), name="admin-inquiry-list"),
]