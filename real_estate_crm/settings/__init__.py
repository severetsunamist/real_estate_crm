from .base import *

# Only load development settings in development
try:
    from .development import *
except ImportError:
    pass