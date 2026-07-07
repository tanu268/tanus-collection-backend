from django.urls import path
from .views import SiteSettingsView

urlpatterns = [
    path("admin/settings/", SiteSettingsView.as_view(), name="admin-site-settings"),
]
