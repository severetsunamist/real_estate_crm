from .base import *

DEBUG = True

# Debug Toolbar configuration
INSTALLED_APPS += ['debug_toolbar', 'django_extensions']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Debug Toolbar settings
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# Use local storage in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'