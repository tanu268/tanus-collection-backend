from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    WishlistListView, WishlistAddView, WishlistRemoveView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),

    path("wishlist/", WishlistListView.as_view(), name="wishlist-list"),
    path("wishlist/add/", WishlistAddView.as_view(), name="wishlist-add"),
    path("wishlist/<slug:slug>/", WishlistRemoveView.as_view(), name="wishlist-remove"),
]
