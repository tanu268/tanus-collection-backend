"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.authtoken import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/", include("apps.accounts.urls")), 
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.inquiries.urls")),
    path("api/", include("apps.activity_log.urls")),
    path('api/admin/login/', views.obtain_auth_token, name='api_login'),
    path("api/", include("apps.gallery.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Stopgap so uploaded images actually load in production. Django serving
    # files itself isn't ideal at scale, but it's fine for this app's traffic
    # today — see the note in settings/production.py about moving MEDIA_ROOT
    # to persistent/Blob storage, which matters more than this line does.
    urlpatterns += [
        path(
            "media/<path:path>",
            static_serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
