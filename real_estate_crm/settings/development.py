from .base import *

DEBUG = True

# Development-specific settings
INTERNAL_IPS = ['127.0.0.1']

# Ensure local storage in development
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Optional: Add debug toolbar
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')