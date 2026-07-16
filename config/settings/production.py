from .base import *

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