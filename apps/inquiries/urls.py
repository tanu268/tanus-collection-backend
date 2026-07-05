from django.urls import path
from .views import (
    InquiryCartListView, InquiryCartAddView, InquiryCartRemoveView,
    InquiryCartClearView, InquirySubmitView, InquiryAdminListView,
    InquiryAdminStatusUpdateView,
)

urlpatterns = [
    path("inquiries/cart/", InquiryCartListView.as_view(), name="inquiry-cart-list"),
    path("inquiries/cart/add/", InquiryCartAddView.as_view(), name="inquiry-cart-add"),
    path("inquiries/cart/clear/", InquiryCartClearView.as_view(), name="inquiry-cart-clear"),
    path("inquiries/cart/<slug:slug>/", InquiryCartRemoveView.as_view(), name="inquiry-cart-remove"),
    path("inquiries/submit/", InquirySubmitView.as_view(), name="inquiry-submit"),

    path("admin/inquiries/", InquiryAdminListView.as_view(), name="admin-inquiry-list"),
    path("admin/inquiries/<int:pk>/status/", InquiryAdminStatusUpdateView.as_view(), name="admin-inquiry-status"),
]
