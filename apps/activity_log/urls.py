from django.urls import path
from .views import ActivityLogListView

urlpatterns = [
    path("admin/activity-log/", ActivityLogListView.as_view(), name="admin-activity-log"),
]