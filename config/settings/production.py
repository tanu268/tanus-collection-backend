from .base import *
import os

DEBUG = False
# ALLOWED_HOSTS, DB config, etc. will be filled from environment variables

# whitenoise serves static files directly from Django/gunicorn — useful on
# hosts like Render/Railway that don't have PythonAnywhere's built-in static
# file mapping. Harmless to leave on for PythonAnywhere too.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + [m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware']

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# The app itself runs from an ephemeral, per-deployment folder on Azure App
# Service (Linux/Oryx builds unpack to something like /tmp/<hash>, which gets
# wiped on every restart or redeploy). BASE_DIR / "media" would live inside
# that same ephemeral folder, so anything admins upload disappears soon after.
# Azure App Service keeps /home persistent across restarts and deploys, so
# point FileSystemStorage's media root there instead.
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/home/media"))
